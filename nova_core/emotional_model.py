# emotional_model.py
from rx import operators as ops

class EmotionalPhysics:
    def __init__(self, ucp, nova_core):
        self.ucp = ucp
        self.nova_core = nova_core
        
        # Stress decay rate: 5% per minute
        self.STRESS_DECAY = 0.00083  # Per second
        
        # Subscribe to context updates
        self.ucp.context_stream.pipe(
            ops.throttle_first(1)
        ).subscribe(self.update_stress)

    def update_stress(self, context):
        current = self.nova_core.emotional_state.value
        new_stress = current['stress']
        
        # Stressors
        new_stress += context.get('system', {}).get('cpu_usage', 0) / 2000
        new_stress += (10 - float(context.get('wallet', {}).get('balance', 10))) / 100
        new_stress -= self.STRESS_DECAY  # Natural decay
        
        # Clamp between 0-1
        new_stress = max(0, min(1, new_stress))
        
        # Update mood
        mood = 'neutral'
        if new_stress > 0.8:
            mood = 'panicked'
        elif new_stress > 0.6:
            mood = 'stressed'
        elif new_stress < 0.2:
            mood = 'playful'

        self.nova_core.emotional_state.on_next({
            'stress': new_stress,
            'mood': mood,
            'focus_energy': current['focus_energy']
        })