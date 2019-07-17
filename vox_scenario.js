require(Modules.CallList); // Enable CallList module
require(Modules.AI);

/* TODO: replace in prod */
let caller_id = "74951505903"; // Rented or verified phone number
let call;
let phone_number;
let message;
let playbackCounter = 0;

// AppEvents.Started dispatched for each CSV record
VoxEngine.addEventListener(AppEvents.Started, function (e) {
  let data = VoxEngine.customData(); // <-- data from CSV string in JSON format
  data = JSON.parse(data);
  phone_number = data.phone_number;
  message = data.message;
  Logger.write(`Calling on ${phone_number}`);
  // Make a call
  call = VoxEngine.callPSTN(phone_number, caller_id);
  // Trying to detect voicemail
  call.addEventListener(CallEvents.AudioStarted, function(){
    AI.detectVoicemail(call)
      .then(voicemailDetected)
      .catch(()=>{
        Logger.write('Voicemail not detected');
      })
  });
  // Add event listeners
  call.addEventListener(CallEvents.Connected, handleCallConnected);
  call.addEventListener(CallEvents.Failed, handleCallFailed);
  call.addEventListener(CallEvents.Disconnected, handleCallDisconnected);
});

function voicemailDetected(e) {
  // Voicemail?
  if (e.confidence >= 75) {
    VoxEngine.CallList.reportError('Voicemail', VoxEngine.terminate);
  }
}

// Call connected successfully
function handleCallConnected(e) {
  connected = true;
  setTimeout(function () {
    e.call.say(`Говорит железная женщина. Дежурному подъем! ${message}`,
      Language.RU_RUSSIAN_FEMALE);
  }, 500);
  e.call.addEventListener(CallEvents.PlaybackFinished, handlePlaybackFinished);
}

function handleCallDisconnected(e) {
  // Tell CallList processor about successful call result
  CallList.reportResult({
    result: true,
    duration: e.duration,
    rating: rating,
  }, VoxEngine.terminate);
}

// Playback finished
function handlePlaybackFinished(e) {
  e.call.removeEventListener(CallEvents.PlaybackFinished, handlePlaybackFinished);
  playbackCounter++;
  // If the message was played 4 times - hangup
  if (playbackCounter === 4) {
    e.call.hangup();
  } else {
    // Play one more time
    setTimeout(function () {
      e.call.say(`Хватит спать! ${message}`,
        Language.RU_RUSSIAN_FEMALE);
      e.call.addEventListener(CallEvents.PlaybackFinished, handlePlaybackFinished);
    }, 2000);
  }
}

function handleCallFailed(e) {
  // Tell CallList processor that we couldn't get call connected
  // depending on the request options it will either try to launch the scenario again after some time
  // or will write the result (failed call) into result_data column of the CSV file with results
  CallList.reportError({
    result: false,
    msg: 'Failed',
    code: e.code
  }, VoxEngine.terminate);
}
