# autonomy_engine.py
import numpy as np

class AutonomyEngine:
    def __init__(self, core):
        self.core = core
        self.q_table = {}  # State -> action -> value
        self.LEARNING_RATE = 0.1
        self.DISCOUNT_FACTOR = 0.95
        
        # Action space
        self.actions = [
            'observe',
            'speak',
            'listen',
            'sleep',
            'speak_warning',
            'throttle_system',
            'execute_transaction'
        ]

    def get_state_hash(self, context):
        """Quantize context into discrete state"""
        # Currently only using emotional state
        return (
            # round(context['system']['cpu_usage'] / 20),  # 0-5
            # round(context['wallet']['balance'] * 10),    # 0-100
            self.core.emotional_state.value['mood']
        )

    def choose_action(self, context):
        # Add priority-based decision making
        priorities = {
            'system_critical': self._check_system_critical(context),
            'user_request': self._check_user_request(context),
            'maintenance': self._check_maintenance_needed(context)
        }
        
        action = max(priorities.items(), key=lambda x: x[1])[0]
        return self._get_action_for_priority(action, context)

    def _check_system_critical(self, context):
        """Check for critical system conditions that need immediate attention"""
        priority = 0
        
        if 'system' in context:
            # High CPU usage is critical
            if context['system'].get('cpu_usage', 0) > 90:
                priority += 0.8
            # Low memory is critical    
            if context['system'].get('memory_available', 100) < 10:
                priority += 0.7
            # High error rate is critical
            if context['system'].get('error_rate', 0) > 0.5:
                priority += 0.9
                
        return priority

    def _check_user_request(self, context):
        """Check for pending user requests or interactions"""
        priority = 0
        
        if 'user' in context:
            # Direct user command takes high priority
            if context['user'].get('pending_command'):
                priority += 0.6
            # User waiting for response
            if context['user'].get('awaiting_response'):
                priority += 0.5
            # Multiple users waiting
            if context['user'].get('active_users', 0) > 1:
                priority += 0.3
                
        return priority

    def _check_maintenance_needed(self, context):
        """Check if routine maintenance tasks are needed"""
        priority = 0
        
        if 'system' in context:
            # Memory cleanup needed
            if context['system'].get('uptime', 0) > 86400:  # 24 hours
                priority += 0.3
            # Cache cleanup needed    
            if context['system'].get('cache_size', 0) > 1000:
                priority += 0.2
            # Regular health check
            if context['system'].get('last_health_check', 0) > 3600:  # 1 hour
                priority += 0.1
                
        return priority

    def _get_action_for_priority(self, priority_type, context):
        """Convert priority type to specific action based on context"""
        action = None
        if priority_type == 'system_critical':
            if context['system'].get('cpu_usage', 0) > 90:
                action = 'throttle_system'
            else:
                action = 'speak_warning'
            
        elif priority_type == 'user_request':
            if context['user'].get('pending_command'):
                action = 'execute_transaction'
            else:
                action = 'speak'
            
        elif priority_type == 'maintenance':
            if context['system'].get('uptime', 0) > 86400:
                action = 'sleep'
            else:
                action = 'observe'
            
        # Emit action event
        self.core.publish_event('autonomous_action', {
            'action': action,
            'priority_type': priority_type,
            'context': context
        })
        
        return action

    def learn(self, old_state, action, reward, new_state):
        old_value = self.q_table.get(old_state, {}).get(action, 0)
        future_rewards = max(self.q_table.get(new_state, {}).values(), default=0)
        
        new_value = (1 - self.LEARNING_RATE) * old_value + \
                    self.LEARNING_RATE * (reward + self.DISCOUNT_FACTOR * future_rewards)
        
        if old_state not in self.q_table:
            self.q_table[old_state] = {}
        self.q_table[old_state][action] = new_value
        
        # Update personality based on reward
        self.core.adapt_personality(reward, new_state)

    def save_state(self, filepath):
        """Save Q-table and learning state to disk"""
        state_data = {
            'q_table': self.q_table,
            'learning_rate': self.LEARNING_RATE,
            'discount_factor': self.DISCOUNT_FACTOR
        }
        np.save(filepath, state_data)