using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {

        public struct ArduinoData
        {
            public double pressure;
            public double temperature;
            public double humidity;
            public int pwmPressureValve;
            public int pwmVacuumValve;
            public bool airPumpStatus;
            public bool pidStatus;
            public double setpoint;
        };
        private ArduinoData _arduinoData;       
        
        private bool _serialIsBusy = false;
        private string _msgFromArduino = "";
        private DateTime _begin;
                              
        
        public Form1()
        {
            InitializeComponent();
        }            
        
        private bool arduinoGetData()
        {
            int attempt = 0;
            do
            {
                if (arduinoSendMessage("a"))
                {
                    _msgFromArduino = _msgFromArduino.Substring(1, _msgFromArduino.Length - 3);
                    List<string> r = _msgFromArduino.Split(';').ToList<string>();
                    if (r[0] == "a")
                    {
                        _arduinoData.pressure = double.Parse(r[1]);
                        _arduinoData.temperature = double.Parse(r[2]);
                        _arduinoData.humidity = double.Parse(r[3]);
                        _arduinoData.pwmPressureValve = int.Parse(r[4]);
                        _arduinoData.pwmVacuumValve = int.Parse(r[5]);
                        _arduinoData.airPumpStatus = (r[6] == "1") ? true : false;
                        _arduinoData.pidStatus = (r[7] == "1") ? true : false;
                        _arduinoData.setpoint = double.Parse(r[8]);
                        return (true);
                    }                    
                }                
                attempt++;
                Console.WriteLine("arduinoGetData...tentativa=" + attempt.ToString());
            } while (attempt < 3);

            MessageBox.Show("Falha na comunicação: arduinoGetData");
            return (false);            
        }

        private void arduinoSetPwmPressureValve(int newValue)
        {
            arduinoSendMessage("c;" + newValue.ToString());            
        }

        private void arduinoSetPwmVacuumValve(int newValue)
        {
            arduinoSendMessage("d;" + newValue.ToString());
        }
             
        private bool arduinoGetPressure()
        {
            int attempt = 0;
            do
            {
                if (arduinoSendMessage("e"))
                {
                    _msgFromArduino = _msgFromArduino.Substring(1, _msgFromArduino.Length - 3);
                    List<string> r = _msgFromArduino.Split(';').ToList<string>();
                    if (r[0] == "e")
                    {
                        _arduinoData.pressure = double.Parse(r[1]);
                        return (true);
                    }
                }
                attempt++;
                Console.WriteLine("arduinoGetPressure...tentativa=" + attempt.ToString());
            } while (attempt < 3);

            MessageBox.Show("Falha na comunicação: arduinoGetPressure");
            return (false);
        }

        private void arduinoEnablePid(bool newValue)
        {
            string s = (newValue) ? "1" : "0";
            arduinoSendMessage("f;" +  s);
        }

        private void arduinoUpdateSetpoint(double newSetpoint)
        {
            string s = newSetpoint.ToString("0.00");
            arduinoSendMessage("g;" + s);
        }

        private void arduinoSetPidParameters(double kp, double ki, double kd)
        {
            string s = kp.ToString("0.0000")+";"+ki.ToString("0.0000")+";"+ kd.ToString("0.0000");
            arduinoSendMessage("h;" + s);
        }
      
        private bool arduinoGetPidParameters()
        {
            int attempt = 0;
            do
            {
                if (arduinoSendMessage("i"))
                {
                    _msgFromArduino = _msgFromArduino.Substring(1, _msgFromArduino.Length - 3);
                    List<string> r = _msgFromArduino.Split(';').ToList<string>();
                    if (r[0] == "i")
                    {
                        tb_read_kp.Text = r[1];
                        tb_read_ki.Text = r[2];
                        tb_read_kd.Text = r[3];
                        return (true);
                    }
                }
                attempt++;
                Console.WriteLine("arduinoSetPidParameters...tentativa=" + attempt.ToString());
            } while (attempt < 3);

            MessageBox.Show("Falha na comunicação: arduinoSetPidParameters");
            return (false);
        }

        private bool arduinoSendMessage(string msg)
        {
            if (!serialPort1.IsOpen)
                serialPort1.Open();

            int attempt = 0;
            do
            {
                if (!_serialIsBusy)
                {
                    _serialIsBusy = true;
                    serialPort1.Write("<" + msg + ">");

                    //aguarda retorno
                    DateTime Tthen = DateTime.Now;
                    do
                    {
                        Application.DoEvents();
                    } while ((Tthen.AddMilliseconds(200) > DateTime.Now) && (_serialIsBusy));

                    if (_msgFromArduino.StartsWith("<") && (_msgFromArduino[_msgFromArduino.Length - 2] == '>'))
                    {
                        return (true);
                    }
                }
                do
                {
                    Application.DoEvents();
                } while (_serialIsBusy) ;
                attempt++;
                Console.WriteLine("arduinoSendData...tentativa=" + attempt.ToString());
            } while (attempt < 100);

            //abortar
            MessageBox.Show("Falha na comunicação após 100 tentativas...arduinoSendData");
            return (false);
        }

        private void wait(double seconds)
        {
            DateTime Tthen = DateTime.Now;
            do
            {
                Application.DoEvents();
            } while (Tthen.AddSeconds(seconds) > DateTime.Now);
        }
                 
        private void bt_airPumpOnOff_Click(object sender, EventArgs e)
        {
            if (bt_airPumpOnOff.Text == "on")
            {
                bt_airPumpOnOff.Text = "off";
            } 
            else
            {
                bt_airPumpOnOff.Text = "on";
            }
        }

        private void bt_pidEnable_Click(object sender, EventArgs e)
        {
            if (bt_pidEnable.Text == "on")
            {
                bt_pidEnable.Text = "off";
                chartPressure.Series[0].Points.Clear();
                chartPressure.Series[1].Points.Clear();
                chartValves.Series[0].Points.Clear();
                chartValves.Series[1].Points.Clear();
                
                _arduinoData.setpoint = Convert.ToDouble(tb_read_setpoint.Text);
                arduinoUpdateSetpoint(_arduinoData.setpoint);
                arduinoEnablePid(true);
            }
            else
            {
                bt_pidEnable.Text = "on";                
                arduinoEnablePid(false);
            }
        }

        private void serialPort1_DataReceived(object sender, System.IO.Ports.SerialDataReceivedEventArgs e)
        {
            _msgFromArduino = serialPort1.ReadLine();
            _serialIsBusy = false;
        }

        private void updateGui(bool updateCharts)
        {
            tb_pressure.Text = _arduinoData.pressure.ToString("0.00");
            tb_temperature.Text = _arduinoData.temperature.ToString("0.00");
            tb_humidity.Text = _arduinoData.humidity.ToString("0.00");
            tb_read_pwmPressureValve.Text = _arduinoData.pwmPressureValve.ToString();
            tb_read_pwmVacuumValve.Text = _arduinoData.pwmVacuumValve.ToString();
            tb_airPumpStatus.Text = (_arduinoData.airPumpStatus) ? "ativada" : "desativada";                      
            tb_pidStatus.Text = (_arduinoData.pidStatus) ? "ativado" : "desativado";

            if (updateCharts)
            {
                chartPressure.Series[0].Points.AddXY((DateTime.Now - _begin).TotalSeconds,_arduinoData.pressure);
                chartPressure.Series[1].Points.AddXY((DateTime.Now - _begin).TotalSeconds, _arduinoData.setpoint);
                chartPressure.Update();
                                
                chartValves.Series[0].Points.AddXY((DateTime.Now - _begin).TotalSeconds,_arduinoData.pwmPressureValve);
                chartValves.Series[1].Points.AddXY((DateTime.Now - _begin).TotalSeconds,_arduinoData.pwmVacuumValve);
                chartValves.Update();
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            arduinoGetData();
            updateGui(false);
            arduinoGetPidParameters();
        }

        private void bt_set_pwmPressureValve_Click(object sender, EventArgs e)
        {
            arduinoSetPwmPressureValve(Convert.ToInt32(num_set_pwmPressureValve.Value));
        }

        private void bt_set_pwmVacuumValve_Click(object sender, EventArgs e)
        {
            arduinoSetPwmVacuumValve(Convert.ToInt32(num_set_pwmVacuumValve.Value));
        }

        private void bt_setPressureAxis_Click(object sender, EventArgs e)
        {
            chartPressure.ChartAreas[0].AxisY.Maximum = (double)num_ymax.Value;
            chartPressure.ChartAreas[0].AxisY.Minimum = (double)num_ymin.Value;
        }

        private void bt_setPidCoefficients_Click(object sender, EventArgs e)
        {
            double kp = double.Parse(tb_set_kp.Text);
            double ki = double.Parse(tb_set_ki.Text);
            double kd = double.Parse(tb_set_kd.Text);
            arduinoSetPidParameters(kp, ki, kd);
            arduinoGetPidParameters();            
        }
                
        private void bt_set_setpoint_Click(object sender, EventArgs e)
        {
            arduinoUpdateSetpoint(Convert.ToDouble(tb_set_setpoint.Text));            
        }   
              
        private void risePressure(double riseTimeInSecs, double finalPressure)
        {
           
            arduinoGetData();
            if (!_arduinoData.pidStatus)
            {
                arduinoUpdateSetpoint(_arduinoData.pressure);
                arduinoEnablePid(true);
            }
           
            double coefAngular = (finalPressure - _arduinoData.pressure) / (riseTimeInSecs - 0);
            double coefLinear = finalPressure - coefAngular * riseTimeInSecs;

            DateTime stageStartTime = DateTime.Now;
            
            do
            {
                arduinoGetData();
                updateGui(true);

                double elapsedSecs = (DateTime.Now - stageStartTime).TotalSeconds;
                double newSetpoint = Math.Round((coefAngular * elapsedSecs + coefLinear) * 5, MidpointRounding.AwayFromZero) / 5;
                if (newSetpoint != _arduinoData.setpoint)
                    arduinoUpdateSetpoint(newSetpoint);
                
                wait(2);
            } while (((DateTime.Now - stageStartTime).TotalSeconds) <= riseTimeInSecs);        
        }

        private void maintainSteadyPressure(double setpoint, double durationInSecs)
        {
            DateTime stageStartTime = DateTime.Now;           
            arduinoUpdateSetpoint(setpoint);
            do
            {
                arduinoGetData();
                updateGui(true);
                wait(2);
            } while (((DateTime.Now - stageStartTime).TotalSeconds) <= durationInSecs);
        }

        private void bt_runExperiment_Click(object sender, EventArgs e)
        {
            double riseTimeRefPressure = Convert.ToDouble(tb_riseTime_refPressure.Text);
            double riseTimeTestPressure = Convert.ToDouble(tb_riseTime_testPressure.Text);
            double timeSteadyRefPressure = Convert.ToDouble(tb_time_steadyRefPressure.Text);
            double timeSteadyTestPressure = Convert.ToDouble(tb_time_steadyTestPressure.Text);
            double pRef = Convert.ToDouble(tb_pRef.Text);
            double pTest = Convert.ToDouble(tb_pTest.Text);
            _begin = DateTime.Now;
                       
            arduinoSetPidParameters(41.11, 3.625, 0);

            listBox1.Items.Clear();
            listBox1.Items.Add("Rampa 1: " + DateTime.Now);            
            risePressure(riseTimeRefPressure, pRef);

            listBox1.Items.Add("Estável 1: " + DateTime.Now);           
            maintainSteadyPressure(pRef, timeSteadyRefPressure);

            listBox1.Items.Add("Rampa 2: " + DateTime.Now);
            risePressure(riseTimeTestPressure, pTest);

            listBox1.Items.Add("Estável 2: " + DateTime.Now);
            maintainSteadyPressure(pTest, timeSteadyTestPressure);

            arduinoSetPwmPressureValve(0);
            Console.WriteLine("fim");
        }

        private void tb_cancelExperiment_Click(object sender, EventArgs e)
        {
            arduinoEnablePid(false);
        }
    }
}
