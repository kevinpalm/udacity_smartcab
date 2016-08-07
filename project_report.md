
**QUESTION 1**: Observe what you see with the agent's behavior as it
takes random actions. Does the smartcab eventually make it to the
destination? Are there any other interesting observations to note?

**ANSWER 1**: When the agent is taking random actions, I notice that the
rewards are mostly negative. It looks like the agent runs a lot of red
lights, cuts other drivers off, ect. While I was watching the agent
never arrived at a target destination, but taking random actions could
theoretically get the agent there. There would just be a lot of luck
involved. I also notice that when the agent goes off the side of the
map, it appears on the opposite side - so this grid is actually a
flattened sphere.

**QUESTION 2**: What states have you identified that are appropriate for
modeling the smartcab and environment? Why do you believe each of these
states to be appropriate for this problem?

**ANSWER 2**: I've defined the state as a list: the light color, if
there is any traffic surrounding the car, which direction the planner is
directing the agent, and a binned representation of the deadline. The
the deadline bins should be 0-3: state 1, 4-8: state 2, 9-16: state 3,
17+: state 4.

My logic for including all of these components in state are:

* Light color - important for yielding
* oncoming front - also important for yielding
* oncoming left - yielding again
* oncoming right - yielding
* planner direction - important for getting to (or avoiding) the target
* deadline bins - provide tiers for how rushed the agent is

**OPTIONAL**: How many states in total exist for the smartcab in this
environment? Does this number seem reasonable given that the goal of
Q-Learning is to learn and make informed decisions about each state? Why
or why not?

**OPTIONAL ANSWER**: There are 192 unique states possible given my
definition of state. I feel like this is definitely on the high end of
what's a reasonable number of possible states for this relatively simple
simulation, but I'm going to go for it and see how it goes. My hope is
that the more complex representation of the world will pay off in the
end, despite no doubt taking a longer time for the agent to learn.