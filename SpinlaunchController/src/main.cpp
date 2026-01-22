#include <WiFi.h>
#include <WebServer.h>
#include "driver/mcpwm.h"
#include "esp_system.h"

// =====================================================
// WLAN
// =====================================================
const char* ssid = "SpinLauncher";
const char* password = "12345678";
WebServer server(80);

// =====================================================
// Pins
// =====================================================
const int PIN_HALL  = 35;
const int PIN_SERVO = 18;

// =====================================================
// Servo Pulse (µs)
// =====================================================
const int SERVO_HOME = 1279;
const int SERVO_FIRE = 1130;

// =====================================================
// Timing
// =====================================================
volatile unsigned long actuatorDelayUs = 1000000;
const unsigned long RETURN_DELAY_US    = 5000000;
volatile float actuatorAngleDeg = 0.0;

// =====================================================
// Status / Flags
// =====================================================
volatile bool armEnabled        = false;
volatile bool timerStartedISR   = false;
volatile bool servoFiredISR     = false;

volatile unsigned long lastHallTime = 0;
volatile unsigned long deltaTime    = 0;
volatile bool newHallPulse          = false;

bool servoFired = false;
unsigned long servoFireTimestamp = 0;

// =====================================================
// RPM
// =====================================================
int measuredRPM = 0;
int desiredRPM  = 0;
int tolRPM      = 5;

// =====================================================
// Hardware Timer
// =====================================================
hw_timer_t* fireTimer = nullptr;

void updateActuatorDelay() {
  if (measuredRPM <= 0) return;

  unsigned long revolutionTimeUs = 60000000UL / measuredRPM;
  actuatorDelayUs = (unsigned long)((actuatorAngleDeg / 360.0f) * revolutionTimeUs);
}

// =====================================================
// ===================== ISR ============================
// =====================================================

// Hall sensor
void IRAM_ATTR ISR_Hall() {
  unsigned long now = micros();
  deltaTime = now - lastHallTime;
  lastHallTime = now;
  newHallPulse = true;

  if (armEnabled && !timerStartedISR &&
      measuredRPM >= (desiredRPM - tolRPM) &&
      measuredRPM <= (desiredRPM + tolRPM)) {

    timerStartedISR = true;
    armEnabled = false;

    timerWrite(fireTimer, 0);
    timerAlarmWrite(fireTimer, actuatorDelayUs, false);
    timerAlarmEnable(fireTimer);
  }
}

// fire
void IRAM_ATTR ISR_FireTimer() {
  mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, SERVO_FIRE);
  servoFiredISR = true;
}

// =====================================================
// HTML
// =====================================================
String getHTML() {
  return R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SpinLauncher</title>
<style>
body { font-family: Arial; text-align:center; margin-top:40px; }
.btn { font-size:22px; padding:15px 40px; color:white; border:none; border-radius:10px; }
.box { font-size:22px; margin:15px; }
input { font-size:20px; padding:5px; width:160px; text-align:center; }
</style>

<script>
async function update() {
  const r = await fetch('/data');
  const d = await r.json();

  document.getElementById('measured').innerText = d.measuredRPM + ' RPM';
  document.getElementById('desired').innerText  = d.desiredRPM  + ' RPM';
  document.getElementById('delay').innerText    = d.delay + ' µs';
  document.getElementById('angle').innerText    = d.angle + ' °';

  const btn = document.getElementById('armBtn');
  btn.innerText = d.arm ? "disarm" : "arm";
  btn.style.backgroundColor = d.arm ? "red" : "green";
}
setInterval(update, 300);
</script>
</head>

<body>
<h1>Rasenmäher</h1>

<button id="armBtn" class="btn" onclick="location.href='/arm'">rasen mähen</button>

<div class="box"><b>Measured RPM</b><div id="measured">0 RPM</div></div>
<div class="box"><b>Desired RPM</b><div id="desired">0 RPM</div></div>
<div class="box"><b>Actuator Delay</b><div id="delay">0 µs</div></div>
<div class="box"><b>Actuator Angle</b><div id="angle">0 °</div></div>

<h3>Set Desired RPM</h3>
<form action="/setRPM">
<input type="number" name="value">
<input type="submit" value="Confirm">
</form>

<h3>Set Actuator Delay (µs)</h3>
<form action="/setDelay">
<input type="number" name="value">
<input type="submit" value="Confirm">
</form>

<h3>Set Actuator Angle (°)</h3>
<form action="/setAngle">
<input type="number" step="0.1" name="value">
<input type="submit" value="Confirm">
</form>

</body>
</html>
)rawliteral";
}

// =====================================================
// HTTP Handler
// =====================================================
void handleRoot() {
  server.send(200, "text/html", getHTML());
}

void handleArm() {
  armEnabled = !armEnabled;
  timerStartedISR = false;
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "");
}

void handleSetRPM() {
  if (server.hasArg("value")) desiredRPM = server.arg("value").toInt();
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "");
}

void handleSetDelay() {
  if (server.hasArg("value")) {
    unsigned long v = server.arg("value").toInt();
    if (v >= 1000 && v <= 10000000) actuatorDelayUs = v;
  }
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "");
}

void handleSetAngle() {
  if (server.hasArg("value")) {
    float v = server.arg("value").toFloat();

    if (v >= 0.0f && v <= 360.0f) {
      actuatorAngleDeg = v;

      if (measuredRPM > 0) {
        unsigned long revTimeUs = 60000000UL / measuredRPM;
        actuatorDelayUs = (unsigned long)((actuatorAngleDeg / 360.0f) * revTimeUs);
      }
    }
  }

  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "");
}


void handleData() {
  String json = "{";
  json += "\"measuredRPM\":" + String(measuredRPM) + ",";
  json += "\"desiredRPM\":"  + String(desiredRPM) + ",";
  json += "\"delay\":"       + String(actuatorDelayUs) + ",";
  json += "\"angle\":"       + String(actuatorAngleDeg) + ",";
  json += "\"arm\":"         + String(armEnabled ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

// =====================================================
// Setup
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(PIN_HALL, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL), ISR_Hall, RISING);

  fireTimer = timerBegin(0, 80, true);
  timerAttachInterrupt(fireTimer, &ISR_FireTimer, false);

  mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0A, PIN_SERVO);
  mcpwm_config_t pwm = {};
  pwm.frequency = 50;
  pwm.cmpr_a = 7.5;
  pwm.counter_mode = MCPWM_UP_COUNTER;
  pwm.duty_mode = MCPWM_DUTY_MODE_0;
  mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &pwm);

  mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, SERVO_HOME);

  WiFi.softAP(ssid, password);
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/arm", handleArm);
  server.on("/setRPM", handleSetRPM);
  server.on("/setDelay", handleSetDelay);
  server.on("/setAngle", handleSetAngle);
  server.on("/data", handleData);
  server.begin();
}

// =====================================================
// Loop
// =====================================================
void loop() {
  server.handleClient();

  if (newHallPulse) {
    newHallPulse = false;
    if (deltaTime > 0) {
      measuredRPM = 60000000UL / deltaTime;
      updateActuatorDelay(); 
    }
  }

  if (servoFiredISR) {
    servoFiredISR = false;
    servoFired = true;
    servoFireTimestamp = micros();
  }

  if (servoFired && micros() - servoFireTimestamp > RETURN_DELAY_US) {
    servoFired = false;
    mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, SERVO_HOME);
  }
}
