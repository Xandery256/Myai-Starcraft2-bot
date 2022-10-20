import sc2
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2
from sc2.ids.upgrade_id import UpgradeId
import random
import cv2
import math
import numpy as np
import sys
import pickle
import time

filename = "state_rwd_action.pkl"
SAVE_REPLAY = True

class Myai(BotAI): 
    reward = 0
    async def on_step(self, iteration: int): # on_step is a method that is called every step of the game.
        # Beginning of logic
        reward = 0
        no_action = True
        while no_action:
            try:
                with open('state_rwd_action.pkl', 'rb') as f:
                    state_rwd_action = pickle.load(f)

                    if state_rwd_action['action'] is None:
                        #print("No action yet")
                        no_action = True
                    else:
                        #print("Action found")
                        no_action = False
            except:
                pass

        await self.distribute_workers() # put idle workers back to work

        action = state_rwd_action['action']
        '''
        0: expand (ie: move to next spot, or build to 16 (minerals)+3 assemblers+3)
        1: build barracks (or up to one) (evenly)
        2: build infantry (evenly)
        3: send scout (evenly/random/closest to enemy?)
        4: attack (known buildings, units, then enemy base, just go in logical order.)
        5: retreat (back to base)
        6: research infantry upgrades
        7: wait (do nothing)
        8: build factory (evenly)
        9: build vehicles (evenly)
        '''

        # 0: expand (ie: move to next spot, or build workers)
        if action == 0:
            try:
                found_something = False
                if self.supply_left < 4 and self.supply_cap < 200:
                    # build supply depots. 
                    if self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                        if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                            await self.build(UnitTypeId.SUPPLYDEPOT, near=random.choice(self.townhalls))
                            found_something = True
                if not found_something:
                    for commandcenter in self.townhalls:
                        # get worker count for this commandcenter:
                        worker_count = len(self.workers.closer_than(10, commandcenter))
                        if worker_count < commandcenter.ideal_harvesters or len(self.workers) < 2: # workers limited to resources left there
                            if commandcenter.is_idle and self.can_afford(UnitTypeId.SCV):
                                commandcenter.train(UnitTypeId.SCV)
                                found_something = True
                        # have we built enough refineries?
                        # find vespene geysers
                        for geyser in self.vespene_geyser.closer_than(10, commandcenter):
                            # build refinery if there isn't one already:
                            if not self.can_afford(UnitTypeId.REFINERY):
                                break
                            if not self.structures(UnitTypeId.REFINERY).closer_than(2.0, geyser).exists:
                                await self.build(UnitTypeId.REFINERY, geyser)
                                found_something = True
                if not found_something:
                    if self.already_pending(UnitTypeId.COMMANDCENTER) == 0 and self.can_afford(UnitTypeId.COMMANDCENTER):
                        await self.expand_now()
            except Exception as e:
                print(e)
        #1: build barracks (or up to one) (evenly)
        elif action == 1:
            try:
                cc = random.choice(self.townhalls)
                # if we can afford it:
                if self.can_afford(UnitTypeId.BARRACKS) and self.already_pending(UnitTypeId.BARRACKS) == 0:
                    # build BARRACKS
                    pos = cc.position.towards(self.enemy_start_locations[0], random.randrange(3,10))
                    await self.build(UnitTypeId.BARRACKS, near=pos)
            except Exception as e:
                print(e)
        #2: build army (random barracks)
        elif action == 2:
            try:
                if self.can_afford(UnitTypeId.MARINE):
                    for bar in self.structures(UnitTypeId.BARRACKS).ready.idle:
                        if self.can_afford(UnitTypeId.MARINE):
                            bar.train(UnitTypeId.MARINE)
            
            except Exception as e:
                print(e)
        #3: send scout
        elif action == 3:
            # are there any idle workers:
            try:
                self.last_sent
            except:
                self.last_sent = 0
            # if self.last_sent doesnt exist yet:
            if (iteration - self.last_sent) > 200:
                try:
                    if self.units(UnitTypeId.SCV).idle.exists:
                        # pick one of these randomly:
                        worker = random.choice(self.units(UnitTypeId.SCV).idle)
                    else:
                        worker = random.choice(self.units(UnitTypeId.SCV))
                    # send worker towards enemy base:
                    worker.attack(self.enemy_start_locations[0])
                    self.last_sent = iteration
                except Exception as e:
                    pass
        #4: attack (known buildings, units, then enemy base, just go in logical order.)
        elif action == 4:
            try:
                # take army and attack!
                # for unit in self.units(UnitTypeId.MARINE).idle:
                for unit in self.units().idle:
                    # if we can attack:
                    if self.enemy_units.closer_than(7, unit):
                        # attack!
                        unit.attack(random.choice(self.enemy_units.closer_than(7, unit)))
                    # if we can attack:
                    elif self.enemy_structures.closer_than(7, unit):
                        # attack!
                        unit.attack(random.choice(self.enemy_structures.closer_than(7, unit)))
                    # any enemy units:
                    elif self.enemy_units:
                        # attack!
                        unit.attack(random.choice(self.enemy_units))
                    # any enemy structures:
                    elif self.enemy_structures:
                        # attack!
                        unit.attack(random.choice(self.enemy_structures))
                    # if we can attack:
                    elif self.enemy_start_locations:
                        # attack!
                        unit.attack(self.enemy_start_locations[0])
            except Exception as e:
                print(e)
        #5: retreat (back to base)
        elif action == 5:
            if self.units(UnitTypeId.MARINE).amount > 0:
                for marine in self.units(UnitTypeId.MARINE):
                    ccpos = []
                    for cc in self.townhalls:
                        ccpos.append(cc.position)
                    avepos = Point2.center(ccpos) if len(ccpos) > 0 else self.start_location
                    pos = avepos.position.towards(self.enemy_start_locations[0], random.randrange(5,10))
                    marine.move(pos)
        #6: research infantry upgrades
        elif action == 6:
            if self.structures(UnitTypeId.ENGINEERINGBAY).exists:
                engibay_ready = self.structures(UnitTypeId.ENGINEERINGBAY).ready
                if engibay_ready:
                    if self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
                        self.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
                    elif self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                        self.research(UpgradeId.TERRANINFANTRYARMORSLEVEL1)
                    elif self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2):
                        self.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2)
                    elif self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3):
                        self.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3)
                    elif self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL2) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL2):
                        self.research(UpgradeId.TERRANINFANTRYARMORSLEVEL2)
                    elif self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL3) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL3):
                        self.research(UpgradeId.TERRANINFANTRYARMORSLEVEL3)
            else:
                if self.can_afford(UnitTypeId.ENGINEERINGBAY) and self.already_pending(UnitTypeId.ENGINEERINGBAY) == 0:
                    # build engineering bay
                    pos = self.start_location.position.towards(self.enemy_start_locations[0], random.randrange(1,10))
                    await self.build(UnitTypeId.ENGINEERINGBAY, near=pos)
            if not self.structures(UnitTypeId.ARMORY).exists and self.can_afford(UnitTypeId.ARMORY) and self.already_pending(UnitTypeId.ARMORY) == 0:
                # build Armory
                pos = self.start_location.position.towards(self.enemy_start_locations[0], random.randrange(1,10))
                await self.build(UnitTypeId.ARMORY, near=pos)
        #7: do nothing
        elif action == 7:
            waiting = 0
        #8: build factory (or up to one) (evenly)
        elif action == 8:
            try:
                cc = random.choice(self.townhalls)
                if self.can_afford(UnitTypeId.FACTORY) and self.already_pending(UnitTypeId.FACTORY) == 0:
                    # build FACTORY
                    pos = cc.position.towards(self.enemy_start_locations[0], random.randrange(2,10))
                    await self.build(UnitTypeId.FACTORY, near=pos)
                # for factory in self.structures(UnitTypeId.FACTORY):
                #     if self.can_afford(UnitTypeId.TECHLAB):
                #         await factory.train(UnitTypeId.TECHLAB)
            except Exception as e:
                print(e)
        #9: build army (random FACTORY)
        elif action == 9:
            try:
                # if self.can_afford(UnitTypeId.SIEGETANK):
                #     for fact in self.structures(UnitTypeId.FACTORY).ready.idle:
                #         if self.can_afford(UnitTypeId.SIEGETANK):
                #             fact.train(UnitTypeId.SIEGETANK)
                if self.can_afford(UnitTypeId.HELLION):
                    for fact in self.structures(UnitTypeId.FACTORY).ready.idle:
                        if self.can_afford(UnitTypeId.HELLION):
                            fact.train(UnitTypeId.HELLION)
            
            except Exception as e:
                print(e)
        

        map = np.zeros((self.game_info.map_size[0], self.game_info.map_size[1], 3), dtype=np.uint8)

        # draw the minerals:
        for mineral in self.mineral_field:
            pos = mineral.position
            c = [175, 255, 255]
            fraction = mineral.mineral_contents / 1800
            if mineral.is_visible:
                #print(mineral.mineral_contents)
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
            else:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [20,75,50]  
        # draw the enemy start location:
        for enemy_start_location in self.enemy_start_locations:
            pos = enemy_start_location
            c = [0, 0, 255]
            map[math.ceil(pos.y)][math.ceil(pos.x)] = c
        # draw the enemy units:
        for enemy_unit in self.enemy_units:
            pos = enemy_unit.position
            c = [100, 0, 255]
            # get unit health fraction:
            fraction = enemy_unit.health / enemy_unit.health_max if enemy_unit.health_max > 0 else 0.0001
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
        # draw the enemy structures:
        for enemy_structure in self.enemy_structures:
            pos = enemy_structure.position
            c = [0, 100, 255]
            # get structure health fraction:
            fraction = enemy_structure.health / enemy_structure.health_max if enemy_structure.health_max > 0 else 0.0001
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
        # draw our structures:
        for our_structure in self.structures:
            # if it's a command center:
            if our_structure.type_id == UnitTypeId.COMMANDCENTER:
                pos = our_structure.position
                c = [255, 255, 175]
                # get structure health fraction:
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
            else:
                pos = our_structure.position
                c = [0, 255, 175]
                # get structure health fraction:
                fraction = our_structure.health / our_structure.health_max if our_structure.health_max > 0 else 0.0001
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
        # draw the vespene geysers:
        for vespene in self.vespene_geyser:
            # draw these after buildings, since refinerys go over them. 
            # tried to denote some way that refinery was on top, couldnt 
            # come up with anything. Tried by positions, but the positions arent identical. ie:
            # vesp position: (50.5, 63.5) 
            # bldg positions: [(64.369873046875, 58.982421875), (52.85693359375, 51.593505859375),...]
            pos = vespene.position
            c = [255, 175, 255]
            fraction = vespene.vespene_contents / 2250
            if vespene.is_visible:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
            else:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [50,20,75]
        # draw our units:
        for our_unit in self.units:
            # if it is a worker:
            if our_unit.type_id == UnitTypeId.SCV:
                pos = our_unit.position
                c = [175, 255, 0]
                # get health:
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]
            else:
                pos = our_unit.position
                c = [255, 75 , 75]
                # get health:
                fraction = our_unit.health / our_unit.health_max if our_unit.health_max > 0 else 0.0001
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction*i) for i in c]

        # show map with opencv, resized to be larger:
        # horizontal flip:

        cv2.imshow('map',cv2.flip(cv2.resize(map, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0))
        cv2.waitKey(1)

        if SAVE_REPLAY:
            # save map image into "replays dir"
            cv2.imwrite(f"replays/{int(time.time())}-{iteration}.png", map)

        
        try:
            attack_count = 0
            # iterate through our army:
            for marine in self.units(UnitTypeId.MARINE):
                # if marine is attacking and is in range of enemy unit:
                if marine.is_attacking and marine.target_in_range:
                    if self.enemy_units.closer_than(5, marine) or self.enemy_structures.closer_than(5, marine):
                        # reward += 0.005 # original was 0.005, decent results, but let's 3x it. 
                        reward += 0.015  
                        attack_count += 1
            for hellion in self.units(UnitTypeId.HELLION):
                # if hellion is attacking and is in range of enemy unit:
                if hellion.is_attacking and hellion.target_in_range:
                    if self.enemy_units.closer_than(5, hellion) or self.enemy_structures.closer_than(5, hellion):
                        # reward += 0.005 # original was 0.005, decent results, but let's 3x it. 
                        reward += 0.015  
                        attack_count += 1

        except Exception as e:
            print("reward",e)
            reward = 0

        
        if iteration % 100 == 0:
            print(f"Iter: {iteration}. RWD: {reward}. M: {self.units(UnitTypeId.MARINE).amount}")

        # write the file: 
        data = {"state": map, "reward": reward, "action": None, "done": False}  # empty action waiting for the next one!

        while True:
            try:
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
            except:
                continue
            break

    async def on_building_construction_complete(self, unit: Unit):
        # print(f"building {unit} completed")
        # await self.distribute_workers()
        if unit.name == 'SupplyDepot':
            unit(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

    async def on_unit_destroyed(self, unit_tag: int):
        """
        Override this in your bot class.
        Note that this function uses unit tags and not the unit objects
        because the unit does not exist any more.
        This will event will be called when a unit (or structure, friendly or enemy) dies.
        For enemy units, this only works if the enemy unit was in vision on death.

        :param unit_tag:
        """
        # if 

result = run_game(  # run_game is a function that runs the game.
    maps.get("2000AtmospheresAIE"), # the map the agents will play on
    [Bot(Race.Terran, Myai()), # runs my coded bot with the given race and agent object 
     Computer(Race.Zerg, Difficulty.Easy)], # runs a pre-built computer agent with the given race and difficulty.
    realtime=False,
)

if str(result) == "Result.Victory":
    rwd = 500
else:
    rwd = -500

#print("step punishment: " + step_punishment)

with open("results.txt","a") as f:
    f.write(f"{result}\n")


map = np.zeros((224, 224, 3), dtype=np.uint8)
observation = map
data = {"state": map, "reward": rwd, "action": None, "done": True}  # empty action waiting for the next one!
while True:
    try:
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    except:
        continue
    break
cv2.destroyAllWindows()
cv2.waitKey(1)
time.sleep(3)
sys.exit()