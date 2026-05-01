from gpiozero import PWMLED

led_pwm = PWMLED(20, frequency=100)  # 100 Hz (sin parpadeo)

# Valores 0.0 a 1.0
led_pwm.value = 0.5  # 50% intensidad
led_pwm.value = 0.75  # 75%
led_pwm.value = 0.0  # apagado
led_pwm.value = 1.0  # máximo