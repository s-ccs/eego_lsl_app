import EdigRPC_pb2 as eg

class Device:
  def __init__(self, stub, amplifier_handle):
    """ constructor. will be called by device manager
    """
    self.stub = stub
    self.amplifier_handle = amplifier_handle
    # self.notify_thread_start(None)

  def __del__(self):
    """ destructor. cleans up handle held by grpc server
    """
    try:
      self.stub.Amplifier_Dispose(eg.Amplifier_DisposeRequest(
        AmplifierHandle = self.amplifier_handle,
      ))
    except Exception as e:
      print(f'device __del__ exception: {e}')

  def GetDeviceInformation(self):
    """ returns the same device info used by the device manager to create this device
    """
    return self.stub.Amplifier_GetDeviceInformation(eg.Amplifier_GetDeviceInformationRequest(
      AmplifierHandle = self.amplifier_handle,
    ))

  def GetChannelsAvailable(self):
    """ returns a list of channels that are available on the device
    """
    return self.stub.Amplifier_GetChannelsAvailable(eg.Amplifier_GetChannelsAvailableRequest(
      AmplifierHandle = self.amplifier_handle,
    ))

  def GetSamplingRatesAvailable(self):
    """ returns supported sampling rates
    """
    return self.stub.Amplifier_GetSamplingRatesAvailable(eg.Amplifier_GetSamplingRatesAvailableRequest(
      AmplifierHandle = self.amplifier_handle,
    ))

  def GetRangesAvailable(self):
    """ returns supported ranges for referential and bipolar/aux channels
    """
    return self.stub.Amplifier_GetRangesAvailable(eg.Amplifier_GetRangesAvailableRequest(
      AmplifierHandle = self.amplifier_handle,
    ))

  def SetMode(self, mode, rate, stim_params):
    """ switches the device into streaming mode, or idle if streaming needs to stop
        the function tries its best to set all default values needed for streaming
    """
    ranges_available = self.GetRangesAvailable()
    ranges = {}
    for r in [eg.ChannelPolarity.Referential, eg.ChannelPolarity.Auxiliary, eg.ChannelPolarity.Bipolar]:
      if r in ranges_available.RangeMap and ranges_available.RangeMap[r].Values != None and len(ranges_available.RangeMap[r].Values)>0:
        ranges[r] = ranges_available.RangeMap[r].Values[0]

    self.stub.Amplifier_SetMode(eg.Amplifier_SetModeRequest(
      AmplifierHandle = self.amplifier_handle,
      Mode = mode,
      StreamParams = eg.StreamParams(
        ActiveChannels = list(range(len(self.GetChannelsAvailable().ChannelList))),
        Ranges = ranges,
        SamplingRate = rate,
        BufferSize = 10_000,
        DataReadyPercentage = 1,
      ),
      #StimParams=stim_params
    ))

  def GetFrame(self):
    """ gets data from the amplifier.

        may throw an exception if there is a problem with the data stream
    Returns:
        a list of frames. Each frame contains a Matrix object with cols, rows and values
    """

    return self.stub.Amplifier_GetFrame(eg.Amplifier_GetFrameRequest(
      AmplifierHandle = self.amplifier_handle,
   ))

  def StartOutputTrigger(self, channels):
    """ if supported by the device, starts the output trigger for a channel list. most often only channel 0
    """
    return self.stub.Amplifier_StartOutputTrigger(eg.Amplifier_StartOutputTriggerRequest(
      AmplifierHandle = self.amplifier_handle,
      Channels = channels
   ))

  def StopOutputTrigger(self, channels):
    """ if supported by the device, stops the output trigger for a channel list. most often only channel 0
    """
    return self.stub.Amplifier_StopOutputTrigger(eg.Amplifier_StopOutputTriggerRequest(
      AmplifierHandle = self.amplifier_handle,
      Channels = channels
   ))

  def SetStimulationParams(self, stim_params):
    """ if supported by the device, sets the updates stimulation parameters
    """
    return self.stub.Amplifier_SetStimulationParameters(eg.Amplifier_SetStimulationParametersRequest(
      AmplifierHandle = self.amplifier_handle,
      StimlationParams = stim_params
   ))

  def StartStimulation(self, channels):
    """ if supported by the device, starts the stimulation for a channel list. most often only channel 0
    """
    return self.stub.Amplifier_StartStimulation(eg.Amplifier_StartStimulationRequest(
      AmplifierHandle = self.amplifier_handle,
      Channels = channels
   ))

  def StopStimulation(self, channels):
    """ if supported by the device, stops the stimulation for a channel list. most often only channel 0
    """
    return self.stub.Amplifier_StopStimulation(eg.Amplifier_StopStimulationRequest(
      AmplifierHandle = self.amplifier_handle,
      Channels = channels
   ))
