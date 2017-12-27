from LickSpout import *
from Timer import *
import pygame


class Behavior:
    """ This class handles the behavior variables """
    def __init__(self, logger, params):
        self.resp_int = params['response_interval']
        self.resp_timer = Timer()
        self.resp_timer.start()
        self.logger = logger

    def is_licking(self):
        return False

    def in_position(self):
        return False

    def is_ready(self):
        return False, 0

    def water_reward(self, probe):
        print('Giving Water at probe:%1d' % probe)

    def punish_with_air(self, probe, air_dur=200):
        print('Punishing with Air at probe:%1d' % probe)

    def give_odor(self, odor_idx, odor_dur):
        print('Odor %1d presentation for %d' % (odor_idx, odor_dur))

    def inactivity_time(self):  # in minutes
        return 0

    def cleanup(self):
        pass


class RPBehavior(Behavior):
    """ This class handles the behavior variables for RP """
    def __init__(self, logger, params):
        self.licker = RPLicker(logger)
        self.valves = RPValveControl(logger)
        super(RPBehavior, self).__init__(logger, params)

    def is_licking(self):
        probe = self.licker.lick()
        if self.resp_timer.elapsed_time() < self.resp_int:
            probe = 0
        return probe

    def in_position(self):
        ready, ready_time = self.licker.is_ready()
        return ready, ready_time

    def water_reward(self, probe):
        self.valves.give_liquid(probe)

    def punish_with_air(self, probe, air_dur=200):
        self.valves.give_air(probe, air_dur)

    def give_odor(self, odor_idx, odor_dur):
        self.valves.give_odor(odor_idx, odor_dur)

    def inactivity_time(self):  # in minutes
        return numpy.minimum(self.licker.timer_probe1.elapsed_time(),
                             self.licker.timer_probe2.elapsed_time()) / 1000 / 60

    def cleanup(self):
        self.licker.cleanup()


class DummyProbe(Behavior):
    def __init__(self, logger, params):
        self.lick_timer = Timer()
        self.lick_timer.start()
        self.ready_timer = Timer()
        self.ready_timer.start()
        self.ready = False
        super(DummyProbe, self).__init__(logger, params)

    def in_position(self):
        probe = self.__get_events()
        return probe

    def is_ready(self):
        self.__get_events()
        eltime = self.ready_timer.elapsed_time()
        return self.ready, eltime

    def inactivity_time(self):  # in minutes
        return self.lick_timer.elapsed_time() / 1000 / 60

    def __get_events(self):
        probe = 0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick(1)
                    probe = 1
                    self.lick_timer.start()
                elif event.key == pygame.K_RIGHT:
                    self.logger.log_lick(2)
                    probe = 2
                elif event.key == pygame.K_SPACE and self.ready:
                    self.ready = False
                    print('off position')
                elif event.key == pygame.K_SPACE and not self.ready:
                    self.lick_timer.start()
                    self.ready = True
                    print('in position')
        return probe



