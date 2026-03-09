PROGRAM main
VAR
	temperature : int AT %MW0 := 25;
	production_counter : int AT %MW1 := 0;
	motor_state : bool AT %QX0.0 := TRUE;
END_VAR

production_counter := production_counter + 1;

IF production_counter > 100 THEN
    production_counter := 0;
END_IF;

IF motor_state AND temperature >= 1000 THEN
    motor_state := FALSE;
ELSIF NOT motor_state AND temperature <= 60 THEN
    motor_state := TRUE;
END_IF;

IF motor_state THEN
    temperature := temperature + 1;
ELSE
    temperature := temperature - 1;
END_IF;

END_PROGRAM