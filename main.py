import speech
import time
import serial
from modbus_tk import modbus_rtu
import modbus_tk.defines as cst

def ConnectRelay(PORT):
    """
 此函数为连接串口继电器模块，为初始函数，必须先调用
 :param PORT: USB-串口端口，需要手动填写，须在计算机中手动查看对应端口
 :return: >0 连接成功，<0 连接超时
20
 """
    try:
        # c2s03 设备默认波特率 9600、偶校验、停止位 1
        master = modbus_rtu.RtuMaster(serial.Serial(port=PORT,
                                                    baudrate=9600, bytesize=8,
                                                    parity='E', stopbits=1))
        master.set_timeout(5.0)
        master.set_verbose(True)
        # 读输入寄存器
        # c2s03 设备默认 slave=2, 起始地址=0, 输入寄存器个数 2
        master.execute(2, cst.READ_INPUT_REGISTERS, 0, 2)
        # 读保持寄存器
        # c2s03 设备默认 slave=2, 起始地址=0, 保持寄存器个数 1
        master.execute(2, cst.READ_HOLDING_REGISTERS, 0, 1)  # 这里可以修改需要读取的功能码
        # 没有报错，返回 1
        response_code = 1
    except Exception as exc:
        print(str(exc))
        # 报错，返回<0 并输出错误
        response_code = -1
        master = None
    return response_code, master



def Switch(master, ACTION):
    """
 此函数为控制继电器开合函数，如果 ACTION=ON 则闭合，如果如果 ACTION=OFF 则断开。
 :param master: 485 主机对象，由 ConnectRelay 产生
 :param ACTION: ON 继电器闭合，开启风扇；OFF 继电器断开，关闭风扇。
 :return: >0 操作成功，<0 操作失败
 """
    try:
        if "on" in ACTION.lower():
            # 写单个线圈，状态常量为 0xFF00，请求线圈接通
            # c2s03 设备默认 slave=2, 线圈地址=0, 请求线圈接通即 output_value 不等于 0
            master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=1)
        else:
            # 写单个线圈，状态常量为 0x0000，请求线圈断开
            # c2s03 设备默认 slave=2, 线圈地址=0, 请求线圈断开即 output_value 等于 0
            master.execute(2, cst.WRITE_SINGLE_COIL, 0, output_value=0)
        # 没有报错，返回 1
        response_code = 1
    except Exception as exc:
        print(str(exc))
        # 报错，返回<0 并输出错误
        response_code = -1
    return response_code

response = speech.input("指示开关风扇 开启 关闭 断开连接")
speech.say("你说了" + response)

def callback(phrase, listener):
    if phrase!='阿':
        phrase='关闭'
    if phrase == "断开连接":
        mas = ConnectRelay("COM4")
        listener.stoplistening()
    if phrase == "打开":
        mas = ConnectRelay("COM4")
        Switch(mas[1],"ON")
    if phrase == "关闭":
        mas = ConnectRelay("COM4")
        Switch(mas[1],"OFF")
    print("你说了" + phrase)
    speech.say(phrase)


listener = speech.listenforanything(callback)
while listener.islistening():
    time.sleep(.5)