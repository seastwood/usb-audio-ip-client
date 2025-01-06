This is a Linux GUI for easier control of both USBIP and Pipewire services.

My Specific Use Case:

- I designed this because I want to use multiple USB devices and a microphone while game streaming with Moonlght/Sunshine on devices that don't allow device passthrough.
This allows me to easily use devices like a Steam Controller and a microphone attached to my Raspberry Pie Zero 2 W while streaming with Moonlight on my TV or Phone. And this allows
me to remotely interact on Discord with a push to talk button on the controller.

Special thanks to the developers of USBIP and Pipewire for making this possible.

How to use:
- You must have ssh, Pipewire, and USBIP installed and enabled on the host device.
- Pipewire and USBIP must also be installed and enabled on the client device.
- Download and run the executabe inside the dist folder.
- Add host ip, username, and password.
- If USBIP is set up correctly and USB devices are available on the host, devices should appear.
  - Sometimes you will need to restart the host usbip service to get it to actually work, so I added a button to do that.
- Configure pipewire host sink and client source settings. (The Apply-Enable-Test button will restart Pipewire on the host and client in order to enable the new modules)
  - The only setting necessary to change is the Host Destination IP.
  - You may also want to increase the Audio Rate for better quality, but this may interfere with USBIP devices if set too high.
- If Pipewire is set up correctly and audio devices are available, devices should appear in the list.
  - You will want to link the INPUT device (if one is plugged in) to the SINK device you configured.
    - The configured sink device may not appear without an output device connected to the host.
    - I am using a usb audio adapter with both a separate microphone and speaker plug, on which I only need to have a microphone plugged in.
    - I found that a headset adapter with a headset plugged in works as well.
    - This is not configured to send audio back to the host.
      - I stream the sound output through Moonlight, which will need to be restarted if this was configured through the Moonlight stream. This is necessary to get the Sunshine Sink Streams to re-initialize because we restarted the Pipewire service during the stream.
  - Then click "Restart Client PW" to allow the client to sync with the new host the PW streamed to your new rtp-source input device on the client.

![400256855-8b6d3345-bc59-4f34-8420-3544ef35bbb2](https://github.com/user-attachments/assets/fc5b1639-60f7-4bea-a94e-6283c33fc6bd)

![400256908-05e708e0-0319-4cba-8bcf-bc603a5d5b39](https://github.com/user-attachments/assets/02137f18-eb17-4ec6-9877-8427b8acde61)

![400256894-64af2702-612b-48e0-8abf-1fd99f2e26db](https://github.com/user-attachments/assets/931dbcaf-54c0-4878-9414-56b4f641dd81)

![400256932-3b5e539d-89fa-42e9-b17e-81459cd13d1c](https://github.com/user-attachments/assets/f4dc563a-a164-42b1-a8b7-590ee552a356)

To do:
- Make USBIP Auto-Connect more automatic. (Currently only auto connects when it starts/on refresh)
- Allow automation of Pipewire Links
- Add more Pipewire module control and functionality, such as sending a Client Sink to Host Source.
- Clean up code.
- Improve documentation.
- Refactor Classes and Methods.
- Make more object oriented.
- Better Error Handling
