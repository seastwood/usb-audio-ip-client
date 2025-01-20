This is a Linux GUI for easier control of both USBIP and Pipewire services.

It lets you connect any number of usb devices from another linux host (or multiple hosts) to the machine running this GUI as if it's directly plugged into it. Pipewire is the software directing audio traffic in most linux machines today, and it utilizes that to stream sound between other devices and the device running this GUI. 

My Specific Use Case:

- I designed this because I want to use multiple USB devices and a microphone while game streaming with Moonlght/Sunshine on devices that don't allow device passthrough.
This allows me to easily use devices like a Steam Controller and a microphone attached to my Raspberry Pie Zero 2 W while streaming with Moonlight on my TV or Phone. This also allows
me to remotely interact on Discord with a push to talk button on the controller.

Special thanks to the developers of USBIP and Pipewire for making this possible.

Note: 
- Tested/works on openSUSE. 
- Tested/works on Fedora 41.
- No other distributions tested
- This does not connect to any servers, so you will need to periodically check for updates here and download the new executable.
- The "client" device is the one running the GUI. The host is the device with the usb devices physically plugged into it.

How to use:
- You must have ssh, Pipewire, and USBIP installed, enabled and started on the host device.
  - Make sure the usbip drivers are loaded:
    - `sudo modprobe vhci_hcd`
    - `sudo modprobe usbip_host`
    - To make them load on boot: `sudo nano /etc/modules-load.d/usbip.conf`
      - Add to file: `vhci_hcd` and `usbip_host`
    - usbip needs to be set up as a service `sudo nano /etc/systemd/system/usbipd.service`
      - place in there:
        - ```
          [Unit]
          Description=USB/IP Daemon
          After=network.target

          [Service]
          ExecStart=/usr/sbin/usbipd -D
          Restart=always

          [Install]
          WantedBy=multi-user.target
          ```
        - save, start, and enable it as usbipd.
- Pipewire and USBIP must also be installed, enabled, and started on the client device.
  - Make sure the usbip driver is loaded:
    - `sudo modprobe vhci_hcd`
    - To make them load on boot: `sudo nano /etc/modules-load.d/usbip.conf`
      - Add to file: `vhci_hcd`
  - USBIP requires sudo to connect to devices. You can edit the sudoers file if you trust it (only way to use this gui currently)
    - run: `sudo visudo`
    - Add to bottom of file: `<username> ALL=(ALL) NOPASSWD: /usr/sbin/usbip`
      - replace `<username>` with your username
- If you have trouble, I recommend testing pipewire and usbip connections from the terminal to ensure your set up is working.
- ssh port 20 and usbip pot 3240 must be allowed.
- Download and run the executable in the dist folder.
- Add host ip, username, and password.
- If USBIP is set up correctly and USB devices are available on the host, devices should appear.
  - Sometimes you will need to restart the host usbip service to get it to actually work, so I added a button to do that. Or go to host and check the status of usbipd 'sudo systemctl status usbipd' it should be working and listening on port 3240. I've had this randomly fail and needing to be manually restarted. (haven't looked into why)
- Configure pipewire host sink and client source settings. (The Apply-Enable-Test button will restart Pipewire on the host and client in order to enable the new modules)
  - The only setting necessary to change is the Destination IPs in the Sender and Receiver tabs.
    - In the Sender tab, set it to the other device ip.
    - In the Receiver tab, set it to the GUI device ip.
  - You may also want to adjust the Audio Rate to your preference, but I tried to optimize it.
  - Once this is done, you should have a new input device called "RTP-source-receiver" (or whatever you changed it to) in your computer settings.
  - You should also have a new output device called RTP-sink-sender.
- If Pipewire is set up correctly and audio devices are available, devices should appear in the lists. The following configuration only requires setting these settings on the Host Devices:
  - To stream a microphone from the host, you want to link the INPUT device (if one is plugged in) to the SINK device you configured. Input -> RTP-sink-sender (It will not work the other way around).
    - The configured sink device may not appear without an output device connected to the host.
      - I am using a usb audio adapter with both a separate microphone and speaker plug, on which I only need to have a microphone plugged in.
      - I found that a headset adapter with a headset plugged in works as well.
    - You should see the link appear in the Host Linked Audio Devices list.
    - You should now be recieving sound through your new RTP-source-receiver input device on your pc.
      - If it doesn't, try clicking "Restart Client PW" to allow the client to sync with the new host audio link.
  - To stream sound back to the host device(sending it out of your pc) link the RTP-source-receiver to the output device. RTP-source-receiver -> output. (It will not work the other way around)
  - Note: If you configured this through a Moonlight session, the session will need to be restarted. This is necessary to get the Sunshine Sink Streams to re-initialize because the Pipewire service was restarted during the stream.
- All connections will remain connected even when the GUI is closed. The actual connections are made with USBIP and Pipewire.

![Screenshot From 2025-01-07 20-08-16](https://github.com/user-attachments/assets/ea5cbd55-8f6f-4d33-928f-e8df7631b6f9)
![Screenshot From 2025-01-08 16-04-55](https://github.com/user-attachments/assets/85d69934-299f-412e-8ce5-72dc4dad8ef9)
![Screenshot From 2025-01-08 16-05-51](https://github.com/user-attachments/assets/a03826a1-bd3b-4642-ae19-c1cf1f28d488)
![400256932-3b5e539d-89fa-42e9-b17e-81459cd13d1c](https://github.com/user-attachments/assets/f4dc563a-a164-42b1-a8b7-590ee552a356)

To do:
- Make USBIP Auto-Connect more automatic. (Currently only auto connects when it starts/on refresh)
  - May just add a configurable polling option for this.
- Allow automation of Pipewire Links
- Add more Pipewire module control and functionality, such as sending a Client Sink to Host Source.
- Clean up code.
- Improve documentation.
- Refactor Classes and Methods.
- Make more object oriented.
- Better Error Handling
- More Feedback Messages
