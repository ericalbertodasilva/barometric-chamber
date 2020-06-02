/*
 * PINOS EM USO:
 *  0: RX
 *  1: TX
 *  2: DHT22
 *  3, A4 e A5: Nanoshield ADC
 *  5: Rele da bomba
 *  9: Valvula pressuriza
 *  10: Valvula despressuriza
 *  
 */

#include <Wire.h>             //Biblioteca 1 WIRE
#include <Nanoshield_ADC.h>   //Biblioteca ADC 16 BITS
#include <DHT.h>              //Biblioteca DHT22
#include <TimerOne.h>         //Biblioteca para facilitar controle da frequencia do PWM


/*DHT22*/
#define DHTPIN 2  //Pino do DHT22
#define DHTTYPE DHT22   // DHT 22  (AM2302)
DHT _dht(DHTPIN, DHTTYPE);
struct DHTdata {
  float t; //temperatura
  float h; //umidade do ar
};

/*Nanoshield ADC16bits*/
/*Pinos A4, A5 e 3 sao utilizados pelo nanoshield*/
Nanoshield_ADC _adc;
int _adcChannel_BarometricPressure = 0; 

/*PWM*/
int _pinPressureValve=9;   //Valvula que pressuriza câmara
int _pinVacuumValve=10;    //Valvula que despressuriza câmara
int _pwmPressureValve =0;  //0..1023
int _pwmVacuumValve =0;    //0..1023

int _pinAirPump = 5;       //Rele que aciona bomba

/*Comunicacao serial*/
const byte NUMCHARS = 64;
char _receivedChars[NUMCHARS];
boolean _newMsgReceived = false;

/*Limites de operacao - integridade da câmara e do sensor*/
const float HPA_MAX = 1040;
const float HPA_MIN = 860;

/*Tempo*/
unsigned long _previousMillis = 0;

/*PID*/
struct PidParameters{
  bool enabled;
  double kp;
  double ki;
  double kd;
  double setPoint;
  double outputMax;
  double outputMin;
  double output;
  
  int activeValve;

  double integralTerm;
  double lastPressure;
  double msInterval;
  //double lastUpdate;    //precisaria timer        
};
PidParameters _pid;

//Leitura do sensor de pressão barométrica
//Sensor configurado para operar na faixa de 850 a 1050 hPa (0 a 5 V)
float readBarometricPressure(){  
  float mV = 1000*_adc.readVoltage(_adcChannel_BarometricPressure);
  float hPa = 0.04*mV+850.0; //Equaçao linear para VoutLO=850 hPa e VoutHI=1050hPa
  return (hPa);
}

//Leituras de umidade e temperatura sao retornadas na estrutura DHTdata
DHTdata readDht()
{
  DHTdata data;
  data.t = _dht.readTemperature();
  data.h = _dht.readHumidity();
  if (isnan(data.t) || isnan(data.h)) //verifica se resultados sao validos
  {
      data.h = -1;
      data.t = -1;
  } 
  return(data);
}


//Zera pwm das duas válvulas
void closeValves()
{
  _pwmPressureValve = 0;
  _pwmVacuumValve = 0;
  //analogWrite(pinPressureValve, pwmPressureValve);
  //analogWrite(pinVacuumValve, pwmVacuumValve);  
  Timer1.pwm(_pinPressureValve, _pwmPressureValve);        //controla valvula 
  Timer1.pwm(_pinVacuumValve, _pwmVacuumValve);        
}

/*
 * Arduino recebe: <a>  
 * Arduino envia:  <a;varios campos>
 */
void sendAllData()
{
  DHTdata data = readDht();             //le temperatura e umidade
  float hPa = readBarometricPressure(); //le pressao barometrica
  String statusAirPump = (digitalRead(_pinAirPump))?"1":"0";
  String statusPid = (_pid.enabled)?"1":"0";
  
  //<a;pressao;temperatura;UR;pwmValvulaPressao;pwmValvulaVacuo;statusBomba;statusPid;setpoint>
  String s = "<a;"+String(hPa,2)+";"+String(data.t,2)+";"+String(data.h,2)+";"+String(_pwmPressureValve)+";"+String(_pwmVacuumValve)+";"+statusAirPump+";"+statusPid+";"+String(_pid.setPoint,2)+">";
  
  Serial.println(s);
}

/*
 * Arduino recebe: <b;0/1>  //0: off    1:on
 * Arduino envia:  <b;0/1>
 */
void controlAirPump()
{
  String s = "";
  
  bool newStatus = (_receivedChars[2]=='1')? true: false;
  digitalWrite(_pinAirPump, newStatus); 
  if (newStatus)
    s = "<b;1>"; 
  else
  {
    closeValves(); //se desligou bomba, desliga valvulas
    s = "<b;0>"; 
  }   
  Serial.println(s);
}

/*
 * Arduino recebe: <c;0..1023>  
 * Arduino envia:  <c;0..1023>
 */
void setPwmPressureValve()
{
  String s = "";
  
  //extrair valor da valvula e do novo valor
  char * strtokIndx;
  char tempChars[NUMCHARS];
  strcpy(tempChars, _receivedChars);
  strtokIndx = strtok(tempChars,";");   // get the first part - the string
  //strcpy(messageFromPC, strtokIndx);  // copy first part
  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pwmPressureValve = atoi(strtokIndx);         // convert this part to a float

  if (_pwmPressureValve<0) _pwmPressureValve = 0;
  if (_pwmPressureValve>1023) _pwmPressureValve = 1023;

  //analogWrite(pinPressureValve, pwmPressureValve);
  Timer1.pwm(_pinPressureValve, _pwmPressureValve);        //controla valvula    
    
  s = "<c;"+String(_pwmPressureValve)+">"; 
  Serial.println(s);  
}

/*
 * Arduino recebe: <d;0..1023>  
 * Arduino envia:  <d;0..1023>
 */
void setPwmVacuumValve()
{
  String s = "";
  
  //extrair valor da valvula e do novo valor
  char * strtokIndx;
  char tempChars[NUMCHARS];
  strcpy(tempChars, _receivedChars);
  strtokIndx = strtok(tempChars,";");   // get the first part - the string
  //strcpy(messageFromPC, strtokIndx);  // copy first part
  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pwmVacuumValve = atoi(strtokIndx);         // convert this part to a float

  if (_pwmVacuumValve<0) _pwmVacuumValve = 0;
  if (_pwmVacuumValve>1023) _pwmVacuumValve = 1023;

  //analogWrite(pinVacuumValve, pwmVacuumValve);  
  Timer1.pwm(_pinVacuumValve, _pwmVacuumValve);        //controla valvula    
    
  s = "<d;"+String(_pwmVacuumValve)+">"; 
  Serial.println(s);  
}

/*
 * Arduino recebe: <e>  
 * Arduino envia:  <e;xxx.xx>
 */
void sendPressureData()
{
  float hPa = readBarometricPressure(); //le pressao barometrica
  String s = "<e;"+String(hPa,2)+">";
  Serial.println(s);
}

/*
 * Arduino recebe: <f;0/1>  //0: off    1:on
 * Arduino envia:  <f;0/1>
 */
void enablePid()
{
  String s = "";
  
  bool newStatus = (_receivedChars[2]=='1')? true: false;
  _pid.enabled = newStatus; 
  if (newStatus)
    s = "<f;1>"; 
  else
  {    
    s = "<f;0>";
    closeValves();     
    _pid.setPoint = 0;    
    _pid.output = 0;
    _pid.integralTerm = 460;
    _pid.lastPressure = 0;
  }   
  Serial.println(s);
}


/*
 * Arduino recebe: <g;xxxx.xx>  //xxxx.xx -> pressao
 * Arduino envia:  <g;xxxx.xx>
 */
void updateSetpoint()
{
  String s = "";
  
  //extrair valor 
  char * strtokIndx;
  char tempChars[NUMCHARS];
  strcpy(tempChars, _receivedChars);
  strtokIndx = strtok(tempChars,";");   // get the first part - the string
  //strcpy(messageFromPC, strtokIndx);  // copy first part
  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pid.setPoint = atof(strtokIndx);         // convert this part to a float

  if (_pid.setPoint<HPA_MIN) _pid.setPoint = HPA_MIN;
  if (_pid.setPoint>HPA_MAX) _pid.setPoint = HPA_MAX;  

  s = "<g;"+String(_pid.setPoint)+">"; 
  Serial.println(s); 
}

/*
 * Arduino recebe: <h;x.xxxx;x.xxxx;x.xxxx>  //kp;ki;kd
 * Arduino envia:  <h;x.xxxx;x.xxxx;x.xxxx>
 */
void setPidParameters()
{
  String s = "";
  
  //extrair valor 
  char * strtokIndx;
  char tempChars[NUMCHARS];
  strcpy(tempChars, _receivedChars);
  strtokIndx = strtok(tempChars,";");   // get the first part - the string
  //strcpy(messageFromPC, strtokIndx);  // copy first part
  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pid.kp = atof(strtokIndx);         // convert this part to a float

  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pid.ki = atof(strtokIndx);         // convert this part to a float

  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  _pid.kd = atof(strtokIndx);         // convert this part to a float
  
  s = "<h;"+String(_pid.kp)+";"+String(_pid.ki)+";"+String(_pid.kd)+">"; 
  Serial.println(s); 
}

/*
 * Arduino recebe: <i>  
 * Arduino envia:  <i;x.xxxx;x.xxxx;x.xxxx> //kp;ki;kd
 */
void getPidParameters()
{
  String s = ""; 
    
  s = "<i;"+String(_pid.kp)+";"+String(_pid.ki)+";"+String(_pid.kd)+">"; 
  Serial.println(s); 
}


/*
 * Arduino recebe: <j;0/1>  //0=Valvula de pressao ; 1=Valvula de vacuo
 * Arduino envia:  <j;0/1>
 */
void setActiveValve()
{
  String s = "";
  
  //extrair valor 
  char * strtokIndx;
  char tempChars[NUMCHARS];
  strcpy(tempChars, _receivedChars);
  strtokIndx = strtok(tempChars,";");   // get the first part - the string
  //strcpy(messageFromPC, strtokIndx);  // copy first part
  strtokIndx = strtok(NULL, ";");       // this continues where the previous call left off
  int valveOpt = atoi(strtokIndx);         // convert this part to a int

  if (valveOpt == 1)
    _pid.activeValve = _pinVacuumValve;
  else
    _pid.activeValve = _pinPressureValve;
 
  s = "<j;"+String(valveOpt)+">"; 
  Serial.println(s); 
}

/*
 * Atencao: Duas variaveis static... algumas vezes nem toda a mensagem chega 
 * de uma vez. É possível compor a mensagem em mais do que um ciclo do loop
*/
void getSerialMessage() {
    static boolean recvInProgress = false;
    static byte j = 0;
    char startMarker = '<';
    char endMarker = '>';
    char c;

    while (Serial.available() > 0 && _newMsgReceived == false) {
        c = Serial.read();

        if (recvInProgress == true) {
            if (c != endMarker) {
                _receivedChars[j] = c;
                j++;
                if (j >= NUMCHARS) {
                    j = NUMCHARS - 1;
                }
            }
            else {
                _receivedChars[j] = '\0'; // terminate the string
                recvInProgress = false;
                j = 0;
                _newMsgReceived = true;
            }
        }

        else if (c == startMarker) {
            recvInProgress = true;
        }
    }
}

void decodeRequest()
{    
  String s;

  char cmd = _receivedChars[0];

  switch(cmd)
  {
    case '?': //echo
      Serial.println("<?>");
      break;

    case 'a': //envia string com varias informacoes para monitoramento do sistema
      sendAllData();
      break;

    case 'b': //controla bomba 
      controlAirPump();
      break;

    case 'c': //controla valvula que pressuriza
      setPwmPressureValve();
      break;

    case 'd': //controla valvula que despressuriza
      setPwmVacuumValve();
      break;   

    case 'e': //le somente pressao
      sendPressureData();
      break;

    case 'f': //habilita PID
      enablePid();
      break;

    case 'g': //define setpoint
      updateSetpoint();
      break;

    case 'h': //define parametros do controlador PID
      setPidParameters();
      break;

    case 'i':
      getPidParameters();
      break;

    case 'j':
      setActiveValve();
      break;
      
    default:
      Serial.println("<?>");
      break;
  }    
}

double clamp(double variableToClamp)
{
  if (variableToClamp <= _pid.outputMin) { return _pid.outputMin; }
  if (variableToClamp >= _pid.outputMax) { return _pid.outputMax; }
  return variableToClamp;
}

void runPidTask(double currentPressure)
{       
    double error = _pid.setPoint - currentPressure;

    // integral term calculation
    
    //DateTime currentTime = DateTime.Now;
    //TimeSpan timeSinceLastUpdate = currentTime - _pid.lastUpdate;
    //_pid.integralTerm += (_pid.ki * error * timeSinceLastUpdate.TotalSeconds);
    
    double deltaT = _pid.msInterval/1000; //aproximacao de variaçao de tempo para evitar o uso de timer aqui    
    _pid.integralTerm += (_pid.ki * error * deltaT);
    _pid.integralTerm = clamp(_pid.integralTerm);

    // derivative term calculation
    double dInput = currentPressure - _pid.lastPressure;
    //double derivativeTerm = _pid.kd * (dInput / timeSinceLastUpdate.TotalSeconds);
    double derivativeTerm = _pid.kd * (dInput / deltaT);

    // proportional term calcullation
    double proportionalTerm = _pid.kp * error;

    double tempOutput = proportionalTerm + _pid.integralTerm - derivativeTerm;
    
    _pid.output = clamp(tempOutput);
        
    if (_pid.activeValve == _pinPressureValve)
      _pwmPressureValve = _pid.output;
    else if (_pid.activeValve == _pinVacuumValve)
      _pwmVacuumValve = _pid.output;
    
    Timer1.pwm(_pid.activeValve, _pid.output);        //controla valvula 

    _pid.lastPressure = currentPressure;
    //_pid.lastUpdate = currentTime;          
}


void setup() {  
  Serial.begin(57600);
  
  _adc.begin();
  _dht.begin();
  
  pinMode(_pinPressureValve, OUTPUT);  
  pinMode(_pinVacuumValve, OUTPUT);   
  pinMode(_pinAirPump, OUTPUT);   
  digitalWrite(_pinAirPump, LOW);   
  
  Timer1.initialize(3333);  // 3333 us = 300 Hz -> frequencia do PWM 

  _pid.enabled = false;
  _pid.kp = 41.11;
  _pid.ki = 3.625;
  _pid.kd = 0;
  _pid.setPoint = 0;
  _pid.outputMax = 1023;
  _pid.outputMin = 450;
  _pid.output = 0;
  _pid.integralTerm = 460;
  _pid.lastPressure = 0;
  _pid.msInterval = 200;
  _pid.activeValve = _pinPressureValve;
  //_pid.lastUpdate = 0;  
}

void loop() {
  //Monitora serial  
  getSerialMessage();
  if (_newMsgReceived == true) {      
      decodeRequest();    
      _newMsgReceived = false;
  }  

  unsigned long currentMillis = millis();
  if ( currentMillis - _previousMillis >= _pid.msInterval ) 
  {    
    float hPa = readBarometricPressure();  

    if (_pid.enabled)
    {
      if (_pid.lastPressure = 0)
        _pid.lastPressure = hPa;
      runPidTask(hPa);          
    }
     
    //Serial.println("<.>");     
    //Bloco de segurança - integridade da câmara -- nunca pode ultrapassar os limites abaixo -> danifica o sensor
    if ( (hPa < (HPA_MIN-10)) || (hPa > (HPA_MAX+10)) ) //DESLIGA TUDO
    {            
      digitalWrite(_pinAirPump, 0); 
      closeValves();
    } 
    _previousMillis += _pid.msInterval;  
  }  

  
}
