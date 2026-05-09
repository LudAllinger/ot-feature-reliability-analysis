PROGRAM main
VAR
	water_level : int AT %MW0 := 50; (* Water levels of the tank *)
	inlet_valve : bool AT %QX0.0 := FALSE; (* Increases the water level *)
	inlet_flow : int := 0;
	outlet_valve : bool AT %QX0.1 := FALSE; (* Decreases the water level *)
	outlet_flow : int := 0;
	pump : bool AT %QX0.2 := FALSE; (* Another variable that need to be true to decrease the water level *)
	level_alarm : bool AT %QX0.3 := FALSE; (* Alarm if something is wrong *)
	water_demand : int AT %MW1 := 0; (* Demand of water that takes from the water tank *)
	cycle_counter : int := 0; (* A counter to add deviations through MOD *)
	timer : TON; (* A timer for when the commands will execute (every 100ms) *)
	timer_trigger : bool := TRUE;
	noise : int;
END_VAR

timer(IN := timer_trigger, PT := T#100ms);

IF timer.Q THEN
timer_trigger := FALSE;
cycle_counter := cycle_counter + 1;

water_demand := 1 + (cycle_counter MOD 2);

noise := (cycle_counter MOD 5) - 2;

IF inlet_valve THEN
    inlet_flow := inlet_flow + 2;
ELSIF inlet_flow > 0 THEN
    inlet_flow := inlet_flow - 1;
END_IF;

IF outlet_valve AND pump THEN
    outlet_flow := outlet_flow + 1;
ELSIF outlet_flow > 0 THEN
    outlet_flow := outlet_flow - 1;
END_IF;

IF inlet_flow > 5 THEN inlet_flow := 5; END_IF;
IF inlet_flow < 0 THEN inlet_flow := 0; END_IF;

IF outlet_flow > 5 THEN outlet_flow := 5; END_IF;
IF outlet_flow < 0 THEN outlet_flow := 0; END_IF;

water_level := water_level + inlet_flow - outlet_flow - water_demand + noise + 1;

IF water_level < 0 THEN
    water_level := 0;
END_IF;

END_IF;

IF NOT timer.Q THEN
    timer_trigger := TRUE;
END_IF;

IF water_level >= 90 THEN
    inlet_valve := FALSE;
    outlet_valve := TRUE;
    pump := TRUE;

ELSIF water_level <= 50 THEN
    inlet_valve := TRUE;
    outlet_valve := FALSE;
    pump := FALSE;
END_IF;

IF water_level >= 95 THEN
    level_alarm := TRUE;
ELSIF water_level < 85 THEN
    level_alarm := FALSE;
END_IF;

END_PROGRAM