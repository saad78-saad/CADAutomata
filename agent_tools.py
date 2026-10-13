import pythoncom
import win32com.client
import os

class CADClient:
    def __init__(self):
        self.sw_app = None
        self.connect()

    def connect(self):
        pythoncom.CoInitialize()
        try:
            # Connect to active SolidWorks instance or launch one
            self.sw_app = win32com.client.GetActiveObject("SldWorks.Application")
        except Exception:
            # Launch SolidWorks if not already running
            sw_cls = win32com.client.Dispatch("SldWorks.Application")
            self.sw_app = sw_cls
            self.sw_app.Visible = True

    def open_part(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Part not found: {file_path}")
        
        # Open document (Document type 1 = swDocPART)
        error = 0
        warning = 0
        model = self.sw_app.OpenDoc6(file_path, 1, 0, "", error, warning)
        self.sw_app.ActivateDoc3(os.path.basename(file_path), False, 0, error)
        return model

    def inspect_model_features(self, model_doc) -> list:
        """Traverses the feature tree and returns feature names and types."""
        features = []
        feat = model_doc.FirstFeature()
        while feat:
            features.append({
                "name": feat.GetName(),
                "type": feat.GetTypeName2()
            })
            # Traverse sub-features if any
            sub_feat = feat.GetFirstSubFeature()
            while sub_feat:
                features.append({
                    "name": sub_feat.GetName(),
                    "type": sub_feat.GetTypeName2()
                })
                sub_feat = sub_feat.GetNextSubFeature()
            feat = feat.GetNextFeature()
        return features

    def get_dimension_value(self, model_doc, dim_name: str) -> float:
        """Retrieves value of a dimension by its full name (e.g., D1@Sketch1)."""
        display_dim = model_doc.Parameter(dim_name)
        if display_dim:
            dimension = display_dim.GetDimension2()
            return dimension.GetValue3(1, "")[0] # Returns value in meters
        raise ValueError(f"Dimension {dim_name} not found.")

    def update_dimension(self, model_doc, dim_name: str, value_mm: float) -> bool:
        """Updates a dimension value (input in millimeters, converts to meters for SW)."""
        value_m = value_mm / 1000.0
        display_dim = model_doc.Parameter(dim_name)
        if display_dim:
            dimension = display_dim.GetDimension2()
            # SetValue3 parameters: Value, SelectOption, ConfigOption
            dimension.SetSystemValue3(value_m, 1, 1, None)
            return True
        raise ValueError(f"Dimension {dim_name} could not be updated.")

    def rebuild_model(self, model_doc) -> bool:
        """Rebuilds the active model to apply changes."""
        return model_doc.Extension.Rebuild(1) # 1 = swRebuildAll