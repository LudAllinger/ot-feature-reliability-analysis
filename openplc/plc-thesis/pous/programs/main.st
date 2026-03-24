PROGRAM main
VAR
	water_level : int AT %MW0 := 50; (* Water levels of the tank *)
	inlet_valve : bool AT %QX0.0 := FALSE; (* Increases the water level *)
	outlet_valve : bool AT %QX0.1 := FALSE; (* Decreases the water level *)
	pump : bool AT %QX0.2 := FALSE; (* Another variable that need to be true to decrease the water level *)
	alarm : bool AT %QX0.3 := FALSE; (* Alarm if something is wrong *)
	water_demand : int AT %MW1 := 0; (* Demand of water that takes from the water tank *)
	water_chemicals : int AT %MW3 := 50; (* Chemicals in the water *)
	cycle_counter : int AT %MW2 := 0; (* A counter to add deviations through MOD *)
	timer : TON; (* A timer for when the commands will execute (every 100ms) *)
	timer_trigger : bool := TRUE;
END_VAR

timer(IN := timer_trigger, PT := T#100ms);

IF timer.Q THEN
    timer_trigger := FALSE;
    cycle_counter := cycle_counter + 1;

    water_demand := 1 + (cycle_counter MOD 3);
    water_level := water_level - water_demand;
    water_chemicals := 50 + (cycle_counter MOD 5) - 2;


    IF inlet_valve THEN
        water_level := water_level + 3;
    END_IF;

    IF pump AND outlet_valve THEN
        water_level := water_level - 1;
    END_IF;
END_IF;

IF NOT timer.Q THEN
    timer_trigger := TRUE;
END_IF;

IF water_level > 90 THEN
    inlet_valve := FALSE;
    outlet_valve := TRUE;
    pump := TRUE;

ELSIF water_level > 70 THEN
    inlet_valve := FALSE;
    outlet_valve := FALSE;
    pump := FALSE;

ELSIF water_level < 40 THEN
    inlet_valve := TRUE;
    outlet_valve := FALSE;
    pump := FALSE;
END_IF;

IF water_level > 95 THEN
    alarm := TRUE;
ELSIF water_level < 85 THEN
    alarm := FALSE;
END_IF;

IF water_chemicals > 80 THEN
    alarm := TRUE;
END_IF;

IF water_level < 0 THEN
    water_level := 0;
END_IF;

END_PROGRAM