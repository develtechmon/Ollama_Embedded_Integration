# ESP32 Client Chat with Ollama model

## Getting Started

For this to work you have to implement the following 1st, otherwise the communcation between ESp32 to Ollama in G14 laptop wont work.

## Please follow this Step
1. Right-click Ollama in the system tray → Quit (fully quit, don't just close window).
2. Start menu → search "environment variables" → Edit environment variables for your account.
3. New… → Name: OLLAMA_HOST, Value: 0.0.0.0 → OK.
4. New… again → Name: OLLAMA_ORIGINS, Value: * → OK.
5. Relaunch Ollama from Start menu.
6. Find your G14's LAN IP: ipconfig in cmd → look for IPv4 Address under your Wi-Fi adapter (something like 192.168.x.x, or if on hotspot, 10.68.x.x).
7. Sanity test — from your phone's browser on the same WiFi, visit http://<G14_IP>:11434. If you see "Ollama is running", the network side is solved. If you don't, no ESP32 code will save you — fix that first.
   ```
   From browse type this:
   http://10.68.173.137:11434/
   ```

   You will see this output:
   ```
   Ollama is running
   ```
8. Then upload the `ollama_wifi_chat_with_esp32.ino` code attached in this project. Please ensure the `OLLAMA_URL` ip address match to G14 IP4 address as in step `7`.
9. Once done upload, change the Serial Monitor to `New Line` to see the behaviour.
10. From serial monitor, type the chat you want and then press enter. You should see the respond immediately.
