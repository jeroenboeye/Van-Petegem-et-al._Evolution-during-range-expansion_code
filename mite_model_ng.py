# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 10:48:34 2013
@author: Jboeye
2.3 No more selection for dormancy
2.7 Split dormancy in temperatures to go in dormancy and to come out of dormancy
"""

import math as math
import random as rnd
import numpy as np
import sys

def func(x, a, b, c):
    return a*x**2 + b*x + c

class Environment:
    '''Physical environment class that tells you the local temperature and 
    daylength, has to be updated once each day'''
    def __init__(self, 
                 max_season_time, 
                 max_x, 
                 max_y,
                 minimum_viable_t, 
                 max_latitude_effect, 
                 max_season_effect,
                 minimal_temp):
        '''Initialize the temperature class'''
        self.max_season_time = max_season_time
        self.minimum_viable_t = minimum_viable_t
        self.max_y = max_y
        self.minimal_temp = minimal_temp
        self.max_latitude_effect = max_latitude_effect
        self.max_season_effect = max_season_effect
        self.temperature_increasing = True
        self.season_effect = -1 #we start in winter
        
    def set_season_effect(self, time):
        '''This class has to be updated each day and changes the 'season effect'
        using a sinus function'''
        old_season_effect = self.season_effect
        self.season_effect = (round(math.cos(math.pi+2*math.pi * 
                             (time % self.max_season_time)/
                             float(self.max_season_time)), 4))
        if old_season_effect<self.season_effect:
            self.temperature_increasing = True
        else:
            self.temperature_increasing = False
                                                           
    def get_local_temp(self, latitude):
        '''Returns the local temperature, this is influenced by the season 
        effect and the longitudinal position (y)'''
        gradient_temp = self.minimal_temp+(self.max_latitude_effect * 
                     (self.max_y-latitude)/float(self.max_y))
        season_temp = self.season_effect * self.max_season_effect# * (1+0.1025*(latitude/float(self.max_y)))                     
        local_temp = gradient_temp + season_temp
        return local_temp
        
class Mite:
    '''The Mite class only contains mite information, no real processes here 
    except aging'''
    def __init__(self, 
                 patch_nr, 
                 development_trade_off, 
                 dispersal_rate, 
                 in_dormancy_temp,
                 out_dormancy_temp,
                 generation,
                 adult = False,
                 age = 0):
        '''Initialization, information comming from parent or initilization 
        procedure (only first generation)'''
        self.patch_nr = patch_nr
        self.age = age
        self.development_trade_off = development_trade_off
        self.dispersal_rate = dispersal_rate
        self.dormancy = False
        self.adult = adult
        self.development = 0
        self.in_dormancy_temp = in_dormancy_temp
        self.out_dormancy_temp = out_dormancy_temp
        self.winter_aging = 0.01
        self.generation = generation
            
    def develop(self,development_factor):
        self.development += development_factor
        
    def adult_aging(self): 
        '''Procedure to handle traits that change over time'''
        #Pdisp = 0.58-0.122*pl.log(self.resource[0])   
        #relatie gebaseerd op werk Annelies artikel AMF, NEM, maar met 
        #data start; functie verandert niet
        #Pdisp = 1
        #popsize = len(self.population)
        
        if self.dormancy:
            self.age +=  self.winter_aging
        else:
            self.age += 1
            
     
class Patch:    
    '''Class that regulates everything at the local population level'''
    def __init__(self, 
                 dispersal_mortality, 
                 patch_nr, 
                 carrying_c, 
                 mutation_rate,  
                 max_x, 
                 max_y,
                 original_range_limit,
                 minimum_viable_temp):
        '''Initialize'''                     
        self.population = []
        self.patch_nr = patch_nr  
        self.max_x = max_x
        self.max_y = max_y
        self.y_coord = self.patch_nr // self.max_x
        self.x_coord = self.patch_nr % self.max_x
        self.carrying_c = carrying_c
        self.dispersal_mortality = dispersal_mortality
        self.mutation_rate = mutation_rate
        self.minimum_viable_temp = minimum_viable_temp
        if self.y_coord < original_range_limit:
            Patch.initialize_mites(self)
        
    def initialize_mites(self):
        '''Mites are initialised'''
        for i in xrange(self.carrying_c):
            # 30 % of the inital population are juveniles
            if rnd.random()<0.3:
                age = 0
                adult = False
            else:
                # age is 10 days (as an adult) on average
                age = np.random.randint(0,15)
                adult = True
            disp_rate = np.random.uniform(0,0.5)
            in_dormancy_temp = np.random.uniform(10,15)
            out_dormancy_temp = np.random.uniform(10,15)
            #Minimum value (0) is fast development and few total lifetime eggs 
            #(15% less eggs and 13% faster) , max value (1) is slow development
            # and more lifetime eggs (13% slower, 15% more eggs)
            generation = 0
            development_trade_off = rnd.random()
            self.population.append(Mite(self.patch_nr, 
                                        development_trade_off, 
                                        disp_rate, 
                                        in_dormancy_temp,
                                        out_dormancy_temp,
                                        generation,
                                        adult,
                                        age)) 
            
            
    def get_in_dormancy_temp_list(self):
        '''This procedure returns the list of local in dormancy temperatures
        so that an average can be calculated over all y coords'''
        in_dormancy_temp_list = []
        for individual in self.population:
            value = individual.in_dormancy_temp
            in_dormancy_temp_list.append(value)
        return in_dormancy_temp_list    
        
    def get_out_dormancy_temp_list(self):
        '''This procedure returns the list of local out dormancy temperatures
        so that an average can be calculated over all y coords'''
        out_dormancy_temp_list = []
        for individual in self.population:
            value = individual.out_dormancy_temp
            out_dormancy_temp_list.append(value)
        return out_dormancy_temp_list    
              
        
    def get_generation_list(self):
        '''This procedure returns the list of local ages so that an average
        can be calculated over all y coords'''
        generation_list = []
        for individual in self.population:
            value = individual.generation
            generation_list.append(value)
        return generation_list         
        
    def get_average_day_length_dormancy(self):
        '''If individuals are present this procedure calculates the average
        day length triggering dormancy'''
        if len(self.population) > 0:
            summed_value = 0
            for individual in self.population:
                summed_value += individual.min_day_length_dormancy
            average_day_length = summed_value / len(self.population)
        else:
            average_day_length = 'NA'
        return average_day_length
        
    def get_average_dispersal_rate(self):
        '''If individuals are present this procedure calculates the average
        dispersal rate'''
        if len(self.population) > 0:
            summed_value = 0
            for individual in self.population:
                summed_value += individual.dispersal_rate
            dispersal_rate = summed_value / len(self.population)
        else:
            dispersal_rate = 'NA'
        return dispersal_rate    
        
    def get_average_develop_trade_off(self):
        '''If individuals are present this procedure calculates the average
        development speed'''
        if len(self.population) > 0:
            summed_value = 0
            for individual in self.population:
                value = individual.development_trade_off
                if value < 0:
                    value = 0
                elif value > 1:
                    value = 1
                summed_value += value
            develop_trade_off = summed_value / len(self.population)
        else:
            develop_trade_off = 'NA'
        return develop_trade_off
        
    def get_trade_off_list(self):
        '''This procedure returns the total trade off value so that an average
        can be calculated over all y coords'''
        trade_off_list = []
        for individual in self.population:
            value = individual.development_trade_off
            if value < 0:
                value = 0
            elif value > 1:
                value = 1
            trade_off_list.append(value)
        return trade_off_list      
        
    def get_disp_list(self):
        '''This procedure returns the total dispersal value so that an average
        can be calculated over all y coords'''
        disp_list=[]
        for individual in self.population:
            value = individual.dispersal_rate
            if value < 0:
                value = 0
            elif value > 1:
                value = 1
            disp_list.append(value)
        return disp_list    
        
    def get_new_patch_nr(self):
        '''Returns the patch nr of one of the 8 neigbouring cells'''
        y_coord = self.y_coord
        x_coord = self.x_coord
        rndm = np.random.randint(0, 8)
        if rndm ==  0:
            x_coord +=  1
        elif rndm ==  1:
            x_coord -=  1
        elif rndm ==  2:
            y_coord +=  1
        elif rndm ==  3:
            y_coord -=  1
        elif rndm ==  4:
            x_coord +=  1
            y_coord +=  1
        elif rndm ==  5:
            x_coord +=  1
            y_coord -=  1
        elif rndm ==  6:
            x_coord -=  1
            y_coord +=  1
        elif rndm ==  7:
            x_coord -=  1
            y_coord -=  1
        x_coord = x_coord % self.max_x 
        # a torus for now, maybe induce absorbing boundaries
        if y_coord >=  self.max_y:
            y_coord = self.max_y - 1
        elif y_coord < 0:
            y_coord = 0
        return y_coord * self.max_x + x_coord  
        # this is the new patch nr derived from x & y
            
    def get_dispersers(self):
        '''Returns (and removes) a list from the population of those that 
        will disperse'''
        pre_dispersal_pop = self.population[:]
        del self.population[:]
        dispersers = []
        for mite in pre_dispersal_pop:
            if ((mite.age>2) 
            and not (mite.dormancy)
            and (rnd.random()<mite.dispersal_rate)):            
                #mites that are old enough to be fertilized can disperse
                if rnd.random()>self.dispersal_mortality:
                    mite.patch_nr = self.get_new_patch_nr()
                    dispersers.append(mite)            
            else:
                self.population.append(mite) 
                #I put the residents in the local population list, 
                #however it is important to remember that at this point 
                #the dispersers are not assigned to any population, they are 
                #in a list on the metapopulation level
        return dispersers
                        
    def insert_disperser(self, disperser):
        '''Inserts a single disperser in the population'''
        self.population.append(disperser)
            
    def survival_and_reproduction(self, 
                                  local_temp,dev_trade_off_size,
                                  egg_trade_off_size,
                                  temperature_increasing):
        '''Important procedure, if individuals survive they have a chance to 
        reproduce'''
        if len(self.population)>0:
        
            #temperature mortality functions from data in Sabelis 1981
            juv_temperature_mortality = (2.7814642857 
                                     - 0.5080143218 * local_temp
                                     + 0.0353697727 * local_temp ** 2 
                                     - 0.0010715657 * local_temp ** 3
                                     + 0.0000119242 * local_temp ** 4)
                                     
            adult_temperature_mortality = (2.6844642857
                                     - 0.5080143218 * local_temp 
                                     + 0.0353697727 * local_temp ** 2 
                                     - 0.0010715657 * local_temp ** 3
                                     + 0.0000119242 * local_temp ** 4)
                                     
            development_factor = (-0.0000060801 *local_temp**4 
                                  + 0.0002758587*local_temp**3 
                                  - 0.0018772839*local_temp**2 
                                  + 0.0075409434*local_temp 
                                  -0.0913945156)
                                  
            lifetime_potential_n_eggs = (- 287.5238095238 + 44.6797089947 * local_temp
                                         - 1.4562857143 * local_temp ** 2
                                         + 0.0149259259 * local_temp ** 3)
                                         
                                         
            if development_factor < 0:
                development_factor = 0
            if lifetime_potential_n_eggs <0:
                lifetime_potential_n_eggs = 0
        adultpop = self.population[:]
        del self.population[:]
        for mite in adultpop:                
            if not mite.adult:
                #All juveniles die below temp 10
                if local_temp > self.minimum_viable_temp:
                #temperature mortality for juveniles from Sabelis 1981
                    if (rnd.random() > juv_temperature_mortality
                    /(9./(development_factor))):
                        trade_off_on_dev_speed = (1-dev_trade_off_size 
                                                + (1-mite.development_trade_off) 
                                                * dev_trade_off_size*2)
                        if trade_off_on_dev_speed < 1-dev_trade_off_size:
                            trade_off_on_dev_speed = 1-dev_trade_off_size
                        elif trade_off_on_dev_speed > 1+dev_trade_off_size:
                            trade_off_on_dev_speed = 1+dev_trade_off_size
                        mite.develop(development_factor * trade_off_on_dev_speed)
                        #in optimal conditions mites take 9 days to develop
                        if mite.development>=9:
                            mite.adult = True                        
                        self.population.append(mite)
            else:
                mite.adult_aging()
                if (temperature_increasing) and (local_temp>mite.out_dormancy_temp):
                    mite.dormancy = False
                elif (not temperature_increasing) and (local_temp<mite.in_dormancy_temp):
                    mite.dormancy = True

                #calculated from Sabelis 1981
                predicted_adult_lifespan = 5459.7*local_temp**(-1.77)
                random_value = rnd.random()
                #mortality with age function from Bancroft & Margolies 1999
                if (random_value > math.exp(-37.0*math.exp(-0.22*(mite.age)))
                and (random_value > adult_temperature_mortality / predicted_adult_lifespan)): 
                    if local_temp > self.minimum_viable_temp or mite.dormancy:
                        self.population.append(mite)                 
                        #reproduction
                        if not(mite.dormancy):
                            trade_off_on_egg_n = ((1-egg_trade_off_size) 
                                                + mite.development_trade_off
                                                *egg_trade_off_size*2)
                            if trade_off_on_egg_n < 1-egg_trade_off_size:
                                trade_off_on_egg_n = 1-egg_trade_off_size
                            elif trade_off_on_egg_n > 1+egg_trade_off_size:
                                trade_off_on_egg_n = 1+egg_trade_off_size
                            total_eggs = int(np.random.normal(
                           (lifetime_potential_n_eggs*trade_off_on_egg_n*0.666 #multiply with 0.666 because the sex ratio is 2/3 female and males are not modeled here
                            /float(predicted_adult_lifespan)), 1.48))
                            for n_egg in xrange(total_eggs):             
                                #For all offspring check if they mutate on one of the  
                                #two genes and transfer the parent traits into the new 
                                #individual                                
                                self.population.append(Mite(mite.patch_nr, 
                                           self.mutation(mite.development_trade_off),
                                           self.mutation(mite.dispersal_rate),
                                           self.mutation(mite.in_dormancy_temp),
                                           self.mutation(mite.out_dormancy_temp),
                                           mite.generation+1))
        
                        
    def mutation(self, value):
        '''A mutation procudure that returns the (possibly) mutated value'''
        if rnd.random() < self.mutation_rate:
            mutation = np.random.uniform(-0.1, 0.1)    
            # a random nr between -0.1 and 0.1
            value *= 1 + mutation        
        return value        
        
    def compete(self):
        '''Simple competition by deleting all individuals from the list 
        that have an index larger than carrying_c after shuffling'''
        if len(self.population)>self.carrying_c:
            np.random.shuffle(self.population)
            del self.population[self.carrying_c:] 
         
class Metapopulation:
    '''The metapopulation level, contains the physical environment (climate) 
    and all populations'''
    def __init__(self, 
                 dispersal_mortality, 
                 carrying_c, 
                 mutation_rate, 
                 max_x, 
                 max_y, 
                 max_season_time, 
                 max_latitude_effect, 
                 max_season_effect, 
                 minimum_viable_temp,
                 original_range_limit,
                 dev_trade_off_size,
                 egg_trade_off_size,
                 minimal_temp,
                 repeat_n):
        self.carrying_c = carrying_c   
        title  =  'Mite_range_model_no_gradient_cc_%s_disp_m_%s_rl_%s_mut_%s_dto_%s_rto_%s_rep_%s.out'
        title  =  title % (str(carrying_c), 
                         str(dispersal_mortality), 
                         str(original_range_limit), 
                         str(mutation_rate),
                         str(dev_trade_off_size),
                         str(egg_trade_off_size),
                         str(repeat_n))   
        self.dev_trade_off_size = dev_trade_off_size
        self.egg_trade_off_size = egg_trade_off_size                        
        self.output = open(title, "w")
        n_patches = max_x * max_y
        self.patches = []
        self.climate = Environment(max_season_time,
                                   max_x,
                                   max_y, 
                                   minimum_viable_temp, 
                                   max_latitude_effect, 
                                   max_season_effect,
                                   minimal_temp)
        self.init_patches(n_patches, 
                          dispersal_mortality, 
                          mutation_rate, 
                          max_x, 
                          max_y,
                          original_range_limit,
                          minimum_viable_temp)   
    
    def init_patches(self, 
                     n_patches,                     
                     dispersal_mortality,
                     mutation_rate, 
                     max_x,
                     max_y,
                     original_range_limit,
                     minimum_viable_temp):
        '''Here patches are initialised'''                 
        for patch_nr in xrange(n_patches):
            self.patches.append(Patch(dispersal_mortality, 
                                      patch_nr, 
                                      self.carrying_c, 
                                      mutation_rate, 
                                      max_x, 
                                      max_y,
                                      original_range_limit,
                                      minimum_viable_temp))
                                      
    def a_day_in_the_life(self, time, max_x):
        '''What a mite goes through every day, survive? if yes, reproduce?, 
        disperse? if dispersed it is placed back in a patch, afterwards 
        competition takes place.'''
        self.climate.set_season_effect(time)
        metapopdispersers = []
        y_disp_list = []
        y_trade_off_list = []
        y_in_dormancy_temp_list = []
        y_out_dormancy_temp_list = []
        y = 0
        trade_off_in_populated = []
        sd_trade_off_in_populated = []
        in_dormancy_temp_in_populated = []
        sd_in_dormancy_temp_in_populated = []
        out_dormancy_temp_in_populated = []
        sd_out_dormancy_temp_in_populated = []
        disp_in_populated = []        
        sd_disp_in_populated = []
        #average_dens = []
        
        for patch in self.patches:            
            if (time>367) and ((time % 1000 == 0) or ((time % 100 == 0) and (time<1000))) :
                if (patch.y_coord>y):                
                    if len(y_disp_list)>0:
                        in_dormancy_temp_in_populated.append(np.mean(y_in_dormancy_temp_list))
                        sd_in_dormancy_temp_in_populated.append(np.std(y_in_dormancy_temp_list))
                        out_dormancy_temp_in_populated.append(np.mean(y_out_dormancy_temp_list))
                        sd_out_dormancy_temp_in_populated.append(np.std(y_out_dormancy_temp_list))
                        trade_off_in_populated.append(np.mean(y_trade_off_list))
                        sd_trade_off_in_populated.append(np.std(y_trade_off_list))
                        disp_in_populated.append(np.mean(y_disp_list))
                        sd_disp_in_populated.append(np.std(y_disp_list))
                        #average_dens.append(len(y_disp_list)/(float(self.carrying_c*max_x)))
                    else:
                        in_dormancy_temp_in_populated.append('NA')  
                        sd_in_dormancy_temp_in_populated.append('NA')
                        out_dormancy_temp_in_populated.append('NA')  
                        sd_out_dormancy_temp_in_populated.append('NA')                        
                        trade_off_in_populated.append('NA')                       
                        sd_trade_off_in_populated.append('NA')
                        disp_in_populated.append('NA')
                        sd_disp_in_populated.append('NA')
                        #average_dens.append('NA')                        

                    
                    y=patch.y_coord
                    y_disp_list = []
                    y_trade_off_list = []
                    y_in_dormancy_temp_list = []
                    y_out_dormancy_temp_list = []
                y_trade_off_list.extend(patch.get_trade_off_list())
                y_disp_list.extend(patch.get_disp_list())
                y_in_dormancy_temp_list.extend(patch.get_in_dormancy_temp_list())
                y_out_dormancy_temp_list.extend(patch.get_out_dormancy_temp_list())            
                                      
            local_temp = self.climate.get_local_temp(patch.y_coord)             
            patch.survival_and_reproduction(local_temp,self.dev_trade_off_size,self.egg_trade_off_size,self.climate.temperature_increasing)           
            metapopdispersers.extend(patch.get_dispersers())   
            
        #repeat this part for the last y coords (highest row)         
        
        if (time>367) and (time % 10000 == 0) :
            self.write_list_to_output(trade_off_in_populated,'trade_off',time)
            self.write_list_to_output(sd_trade_off_in_populated,'sd_trade_off',time)
            self.write_list_to_output(disp_in_populated,'disp_rate',time)        
            self.write_list_to_output(sd_disp_in_populated,'sd_disp_rate',time) 
            self.write_list_to_output(in_dormancy_temp_in_populated,'dorm_temp_in',time)        
            self.write_list_to_output(sd_in_dormancy_temp_in_populated,'sd_dorm_temp_in',time)
            self.write_list_to_output(out_dormancy_temp_in_populated,'dorm_temp_out',time)        
            self.write_list_to_output(sd_out_dormancy_temp_in_populated,'sd_dorm_temp_out',time)            
            self.write_list_to_output(self.avr_generation_in_populated,'n_gener',time)        
            self.write_list_to_output(self.sd_generation_in_populated,'sd_n_gener',time)                   
                    
        for disperser in metapopdispersers:
            self.patches[disperser.patch_nr].insert_disperser(disperser) 
        total_pop = 0
        for patch in self.patches:
            patch.compete() #round the local population to the carrying capacity
            if time % 10 == 0:
                total_pop += len(patch.population)
        #if time % 10 == 0:
        #    print time, total_pop   
        
    def write_list_to_output(self,target_list,list_name,time):
        self.output.write(str(time)+"\t"+list_name)
        for element in target_list:
            if element!='NA':
                self.output.write("\t%s"%str(round(element, 3)))  
            else:
                self.output.write("\t'NA'")       
        self.output.write("\n")
            
    def winter_toll(self, min_winter_mort, max_winter_mort, max_y):
        self.avr_generation_in_populated=[]
        self.sd_generation_in_populated=[]
        y_generation_list =[]
        y=0
        for patch in self.patches:
            if (patch.y_coord>y):                
                if len(y_generation_list)>0:
                    self.avr_generation_in_populated.append(np.mean(y_generation_list))
                    self.sd_generation_in_populated.append(np.std(y_generation_list))
                else:
                    self.avr_generation_in_populated.append('NA')   
                    self.sd_generation_in_populated.append('NA')   
                y=patch.y_coord
                y_generation_list = []
            y_generation_list.extend(patch.get_generation_list())
            old_pop = patch.population[:]
            del patch.population[:]
            local_winter_mort = (min_winter_mort + 
                                (max_winter_mort-min_winter_mort)
                                *(patch.y_coord/float(max_y)))
            for individual in old_pop:
                if rnd.random()>local_winter_mort:
                    individual.generation = 0
                    #individual.age+=(365*individual.winter_aging)/2
                    patch.population.append(individual)
        

        
class Simulation:
    '''The highest level initialising the metapopulation and looping 
    over time'''
    def __init__(self, 
                 maxtime, 
                 dispersal_mortality, 
                 carrying_c, 
                 mutation_rate, 
                 max_x, 
                 max_y, 
                 max_season_time, 
                 max_latitude_effect, 
                 max_season_effect, 
                 minimum_viable_temp, 
                 original_range_limit,
                 min_winter_mort,
                 max_winter_mort,
                 dev_trade_off_size,
                 egg_trade_off_size,
                 minimal_temp,
                 repeat_n): 
        self.maxtime = maxtime
        self.metapop = Metapopulation(dispersal_mortality, 
                                      carrying_c, 
                                      mutation_rate, 
                                      max_x, 
                                      max_y, 
                                      max_season_time, 
                                      max_latitude_effect, 
                                      max_season_effect, 
                                      minimum_viable_temp, 
                                      original_range_limit,
                                      dev_trade_off_size,
                                      egg_trade_off_size,
                                      minimal_temp,
                                      repeat_n)
        self.time_loop(max_season_time, min_winter_mort, max_winter_mort, max_x, max_y)
            
    def time_loop(self,max_season_time, min_winter_mort, max_winter_mort,max_x, max_y):
        '''The time loop...'''
        for time in xrange(self.maxtime):
            self.metapop.a_day_in_the_life(time, max_x)
            if (time > 1) and (time % max_season_time == 0):
                #self.metapop.climate.max_season_effect = np.random.normal(10,1)
                self.metapop.winter_toll(min_winter_mort, max_winter_mort, max_y)
        self.metapop.output.close()
                
        
    def analyse(self):
        '''Procedure to analyse data'''
        pass
        
if __name__ == '__main__':                
    SIMULATION = Simulation(maxtime = 100002, 
                            dispersal_mortality = float(sys.argv[1]), 
                            carrying_c = int(round(float(sys.argv[2]))), 
                            mutation_rate = float(sys.argv[3]), 
                            max_x = 5, 
                            max_y = 100, 
                            max_season_time = 365, 
                            max_latitude_effect = 0, #how much warmer it is in the extreme south compared to the extreme north
                            max_season_effect = 7.47708, #the amplitude of the cosinus over time, which adds to the local temperature
                            minimum_viable_temp = 10,
                            original_range_limit = int(round(float(sys.argv[4]))),
                            min_winter_mort = 0.5,#perceived in the south
                            max_winter_mort = 0.8,#perceived in the north
                            dev_trade_off_size = float(sys.argv[5]),#the max deviation in both directions (total deviation = x2)
                            egg_trade_off_size = float(sys.argv[6]),#the max deviation in both directions (total deviation = x2)
                            minimal_temp = 10.5,
                            repeat_n = int(round(float(sys.argv[7]))))
                            
#    import cProfile
#    cProfile.run('SIMULATION.time_loop()')
#    print 'Finished !'                            