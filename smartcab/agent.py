import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import math
import operator
import pandas as pd
import matplotlib.pyplot as plt

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint

        # Create an empty dictionary for storing policies
        self.policy = {}

        # Create some lists for summary statistics at the end
        self.turncountlist = []
        self.rewardsumlist = []
        self.reachdestlist = []

        # Set the total turns count to 1.0
        self.totalturns = 1.0


    def reset(self, destination=None):
        self.planner.route_to(destination)

        # Log the last round's stats
        try:
            self.turncountlist.append(self.turncount)
            self.rewardsumlist.append(self.rewardsum)
            self.reachdestlist.append(self.destbool)
        except:
            pass

        # Start a fresh counter for turn count and reward sum
        self.turncount = 0.0
        self.rewardsum = 0.0
        self.destbool = 0.0

    def choose_action(self, state, epsilon=0.2):

        # Check if a policy exists
        if state in self.policy.keys():

            # If so, pick the action
            action = max(self.policy[state].iteritems(), key=operator.itemgetter(1))[0]
            expected = self.policy[state][action]


        else:

            # If not, try and find the most similar example
            try:
                comparisons = {}
                for policy in self.policy.keys():
                    comparisons[policy] = len([i for i in range(len(policy)) if policy[i] == state[i]])
                nearpolicy = max(comparisons.iteritems(), key=operator.itemgetter(1))[0]
                action = max(self.policy[nearpolicy].iteritems(), key=operator.itemgetter(1))[0]
                expected = self.policy[nearpolicy][action]

            # If that doesn't work, just pick a random action for the first encounter with that state
            except:
                action = random.choice([None, "left", "right", "forward"])
                expected = 1.0

        # Pick a random action with (decayed) epsilon likelihood every now and then
        if random.random() <= epsilon/math.sqrt(self.totalturns):
            action = random.choice([None, "left", "right", "forward"])
            try:
                expected = self.policy[state][action]
            except:
                try:
                    expected = self.policy[nearpolicy][action]
                except:
                    expected = 1.0

        return action, expected


    def update_policy(self, action, reward, alpha=0.2, initq=1.0, gamma = 0.2):

        # Get the new state for estimating Q
        newtokey = self.env.sense(self).values()
        newtokey.append(self.planner.next_waypoint())
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

        # Concatenate the separate inputs as the state
        tokey = inputs.values()
        tokey.append(self.next_waypoint)
        self.state = tuple(tokey)

        # Select action according to your policy
        action, expected = self.choose_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # Learn policy based on state, action, reward
        self.update_policy(action, reward)

        # Check if the destination was reached
        if self.env.done == True:
            self.destbool = 1.0

        # Add to turn count
        self.turncount += 1.0
        self.totalturns += 1.0

        # Add to reward sum
        self.rewardsum += reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0001, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    # Output a dataframe for visualizing and summarizing the experiment
    df = pd.DataFrame()
    df["Turns"] = a.turncountlist
    df["Rewards"] = a.rewardsumlist
    df["Destination"] = a.reachdestlist
    df["Rewards per Turn"] = df["Rewards"] / df["Turns"]
    df["Trial"] = df.index

    return df


if __name__ == '__main__':
    # Run multiple trials for a nice smooth graphic
    for i in range(100):
        outdf = run()
        try:
            sumdf = sumdf.append(outdf, ignore_index=True)
        except:
            sumdf = outdf
    df = sumdf.groupby("Trial")[["Rewards per Turn", "Destination"]].mean()
    print "Average Rewards per Turn: {0}\nAverage Destinations Reached: {1}".format(df["Rewards per Turn"].mean(),
                                                                                    df["Destination"].mean())
    ltdf = df.reset_index()
    print "Average Rewards per Turn for the last 10 trials: {0}" \
          "\nAverage Destinations Reached for the last 10 trials: {1}".format(
        ltdf[ltdf["Trial"] >= 90]["Rewards per Turn"].mean(),
        ltdf[ltdf["Trial"] >= 90]["Destination"].mean())


    df.plot()
    plt.savefig("../images/summary_plot.png")

