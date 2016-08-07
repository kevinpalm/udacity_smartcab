import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import math
import operator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # Create an empty dictionary for storing policies
        self.policy = {}

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def choose_action(self, state):

        # Check if a policy exists
        if self.state in self.policy.keys():

            # If so, pick the action
            action = max(self.policy[self.state].iteritems(), key=operator.itemgetter(1))[0]
            expected = self.policy[self.state][action]


        else:

            # If not, try and find the most similar example
            try:
                comparisons = {}
                for policy in self.policy.keys():
                    comparisons[policy] = len([i for i in range(len(policy)) if policy[i]==self.state[i]])
                nearpolicy = max(comparisons.iteritems(), key=operator.itemgetter(1))[0]
                action = max(self.policy[nearpolicy].iteritems(), key=operator.itemgetter(1))[0]
                expected = self.policy[nearpolicy][action]

            # If that doesn't work, just pick a random action for the first encounter with that state
            except:
                action = random.choice([None, "left", "right", "forward"])
                expected = 1.0

        return action, expected


    def update_policy(self, action, reward, alpha=0.1, initq=1.0, gamma = 0.5):
        # Get the new state for estimating Q
        newtokey = self.env.sense(self).values()
        newtokey.extend([self.planner.next_waypoint(), max(min(int(math.sqrt(self.env.get_deadline(self))), 4), 1)])
        newstate = tuple(newtokey)

        # Check if the previous state was already in the policies, otherwise initialize it
        if self.state not in self.policy.keys():
            self.policy[self.state] = {x: initq for x in [None, "left", "right", "forward"]}

        # Check if the new state is in the policies, otherwise initialize it
        if newstate not in self.policy.keys():
            self.policy[newstate] = {x: initq for x in [None, "left", "right", "forward"]}

        # Estimate Q
        nextaction, nextexpected = self.choose_action(newstate)
        qnew = reward + gamma*nextexpected
        qold = self.policy[self.state][action]
        qest = (1-alpha)*qold+alpha*qnew

        # Update the policy
        self.policy[self.state][action] = qest


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Bin up the deadlines using square root, to a maximum of 4 and a minimum of 1
        bindeadline = max(min(int(math.sqrt(deadline)), 4), 1)

        # Concatenate the separate inputs as the state
        tokey = inputs.values()
        tokey.extend([self.next_waypoint, bindeadline])
        self.state = tuple(tokey)

        
        # TODO: Select action according to your policy
        action, expected = self.choose_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.update_policy(action, reward)





        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
