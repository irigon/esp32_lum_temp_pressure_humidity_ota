import ota

try:
    ota.connect_wifi()
    if ota.is_update_needed():
        print("Updating...")
        ota.update()
    else:
        print("No OTA update needed.")
except Exception as e:
    print("OTA update failed:", e)

