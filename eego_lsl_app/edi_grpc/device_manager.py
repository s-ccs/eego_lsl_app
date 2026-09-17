import grpc

import EdigRPC_pb2 as eg
import EdigRPC_pb2_grpc as eg_grpc

import edi_grpc.device

class DeviceManager:
  def __init__(self, channel_address):
    """ constructor

    Args:
        channel_address (string): the address and port of the grpc server. eg: servername.com:3390

    """
    channel=grpc.insecure_channel(channel_address)
    self.stub = eg_grpc.EdigRPCStub(channel)

  def GetDevices(self):
    """ Get a list of devices attached to the grpc server
    """
    v = self.stub.DeviceManager_GetDevices(eg.DeviceManager_GetDevicesRequest())
    return v.DeviceInfoList

  def CreateDevice(self, device_info_list):
    """ creates a device using a number of device info structs retreived by GetDevices
    """
    a = self.stub.Controller_CreateDevice(eg.Controller_CreateDeviceRequest(
      DeviceInfoList = device_info_list,
    ))
    return edi_grpc.device.Device(self.stub, a.AmplifierHandle)
