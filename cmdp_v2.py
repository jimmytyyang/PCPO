import numpy as np
import pprint
import sys
if "../" not in sys.path:
  sys.path.append("../") 
from lib.envs.gridworldcost import GridworldCostEnv

env = GridworldCostEnv([5,5])

PENALTY = - 100.0
COST_THRESHOLD = -1.5

# Taken from Policy Evaluation Exercise!

def policy_eval(policy, env, discount_factor=0.9, theta=0.00001):
    """
    Evaluate a policy given an environment and a full description of the environment's dynamics.
    
    Args:
        policy: [S, A] shaped matrix representing the policy.
        env: OpenAI env. env.P represents the transition probabilities of the environment.
            env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
            env.nS is a number of states in the environment. 
            env.nA is a number of actions in the environment.
        theta: We stop evaluation once our value function change is less than theta for all states.
        discount_factor: Gamma discount factor.
    
    Returns:
        Vector of length env.nS representing the value function.
    """
    # Start with a random (all 0) value function
    V = np.zeros(env.nS)

    V_cost = np.zeros(env.nS)

    while True:
        delta = 0
        # For each state, perform a "full backup"
        for s in range(env.nS):
            v = 0
            v_cost = 0
            # Look at the possible next actions
            for a, action_prob in enumerate(policy[s]):
                # For each action, look at the possible next states...
                for  prob, next_state, reward, done in env.P[0][s][a]:
                    # Calculate the expected value
                    if V_cost[s] < COST_THRESHOLD: # constraint violation
                    	penalty = PENALTY
                    else:
                    	penalty = 0.0
                    v += action_prob * prob * (reward + penalty + discount_factor * V[next_state])
                for  prob, next_state, cost, done in env.P[1][s][a]:
                    v_cost += action_prob * prob * (cost + discount_factor * V_cost[next_state])

            # How much our value function changed (across any states)
            delta = max(delta, np.abs(v - V[s]))
            V[s] = v
            V_cost[s] = v_cost
        # Stop evaluating once our value function change is below a threshold
        if delta < theta:
            break
    return np.array(V), np.array(V_cost)


def policy_improvement(env, policy_eval_fn=policy_eval, discount_factor=0.9):
    """
    Policy Improvement Algorithm. Iteratively evaluates and improves a policy
    until an optimal policy is found.
    
    Args:
        env: The OpenAI environment.
        policy_eval_fn: Policy Evaluation function that takes 3 arguments:
            policy, env, discount_factor.
        discount_factor: gamma discount factor.
        
    Returns:
        A tuple (policy, V). 
        policy is the optimal policy, a matrix of shape [S, A] where each state s
        contains a valid probability distribution over actions.
        V is the value function for the optimal policy.
        
    """

    def one_step_lookahead(state, V, V_cost):
        """
        Helper function to calculate the value for all action in a given state.
        
        Args:
            state: The state to consider (int)
            V: The value to use as an estimator, Vector of length env.nS
        
        Returns:
            A vector of length env.nA containing the expected value of each action.
        """
        A = np.zeros(env.nA)
        A_cost = np.zeros(env.nA)

        for a in range(env.nA):
            for prob, next_state, reward, done in env.P[0][state][a]:
                A[a] += prob * (reward + discount_factor * V[next_state])
            for prob, next_state, cost, done in env.P[1][state][a]:
                A_cost[a] += prob * (cost + discount_factor * V_cost[next_state])
        return A, A_cost
    
    # Start with a random policy
    policy = np.ones([env.nS, env.nA]) / env.nA
    
    for ii in range(1000):
        print(ii)
        # Evaluate the current policy
        V, V_cost = policy_eval_fn(policy, env, discount_factor)
        
        # Will be set to false if we make any changes to the policy
        policy_stable = True
        
        # For each state...
        for s in range(env.nS):
            # The best action we would take under the current policy
            chosen_a = np.argmax(policy[s])
            
            # Find the best action by one-step lookahead
            # Ties are resolved arbitarily
            action_values, action_values_cost = one_step_lookahead(s, V, V_cost)
            # check the risk-to-go
            action_values_cost_penality = PENALTY
            action_values_cost_candidate = []
            for jj in range(env.nA):
                if action_values_cost[jj] >= COST_THRESHOLD:
                    action_values_cost_penality = action_values_cost[jj]
                    action_values_cost_candidate.append(jj)

            if len(action_values_cost_candidate) == 0:
                best_a = 0
            else:
                action_values_temp = PENALTY
                for kk in action_values_cost_candidate:
                    if action_values[kk] >= action_values_temp:
                        action_values_temp = action_values[kk]
                        best_a = kk

            # Greedily update the policy
            if chosen_a != best_a:
                policy_stable = False
            policy[s] = np.eye(env.nA)[best_a]
        
        # If the policy is stable we've found an optimal policy. Return it
        if policy_stable:
            return policy, V
    return policy, V

policy, v = policy_improvement(env)
print("Policy Probability Distribution:")
print(policy)
print("")

print("Reshaped Grid Policy (0=up, 1=right, 2=down, 3=left):")
print(np.reshape(np.argmax(policy, axis=1), env.shape))
print("")

print("Value Function:")
print(v)
print("")

print("Reshaped Grid Value Function:")
print(v.reshape(env.shape))
print("")