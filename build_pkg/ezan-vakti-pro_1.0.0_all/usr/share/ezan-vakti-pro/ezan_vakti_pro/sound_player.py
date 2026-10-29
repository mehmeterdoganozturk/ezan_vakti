import os
import shutil
import subprocess
import threading

class SoundPlayer:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.pre_warning_wav = os.path.join(self.assets_dir, "pre_warning.wav")
        self.ezan_wav = os.path.join(self.assets_dir, "ezan_chime.wav")

        self._current_process = None

    def _play_file(self, filepath: str):
        if not self.storage.config.get("sound_enabled", True):
            return

        if not os.path.exists(filepath):
            return

        def _worker():
            try:
                # Find available player on Wayland/Linux
                player_bin = None
                for candidate in ["paplay", "pw-play", "aplay"]:
                    if shutil.which(candidate):
                        player_bin = candidate
                        break

                if not player_bin:
                    return

                # Stop previous if still playing
                self.stop()

                self._current_process = subprocess.Popen(
                    [player_bin, filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self._current_process.wait()
            except Exception as e:
                print(f"Sound playback error: {e}")
            finally:
                self._current_process = None

        threading.Thread(target=_worker, daemon=True).start()

    def play_pre_warning(self):
        self._play_file(self.pre_warning_wav)

    def play_ezan(self):
        self._play_file(self.ezan_wav)

    def stop(self):
        if self._current_process and self._current_process.poll() is None:
            try:
                self._current_process.terminate()
            except Exception:
                pass
            self._current_process = None
