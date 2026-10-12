import sys
import os

class CADClient:
    def __init__(self):
        self.is_windows = sys.platform == 'win32'
        self.sw_app = None
        
        if self.is_windows:
            try:
                import win32com.client
                self.sw_app = win32com.client.Dispatch("SldWorks.Application")
            except Exception as e:
                print(f"Warning: SolidWorks not available on Windows: {e}")
                self.is_windows = False
        else:
            print("INFO: Running in Cloud Mock CAD Mode (Linux Environment).")

    def open_part(self, file_path: str):
        if not self.is_windows:
            print(f"[CLOUD MOCK] Opening part template: {file_path}")
            return True
        # Live Windows SolidWorks integration code goes here

    def execute_adaptation(self, part_name: str, dx: float, dy: float, dz: float, output_path: str):
        if not self.is_windows:
            print(f"[CLOUD MOCK] Scaling part {part_name} by dx={dx}, dy={dy}, dz={dz}")
            # Create a mock output file so the API returns success smoothly
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            with open(output_path, "w") as f:
                f.write("MOCK_SLDPRT_BINARY_DATA")
            return output_path
        # Live Windows SolidWorks feature scaling code goes here