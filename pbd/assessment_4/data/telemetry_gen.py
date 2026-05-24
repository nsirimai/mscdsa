import pandas as pd
import numpy as np

def generate_assignment_data(n_tractors=250,days=30):
    np.random.seed(42)
    
    profiles = np.random.choice(['Healthy', 'Degrading', 'Critical'], 
                                size=n_tractors, p=[0.7, 0.2, 0.1])
    
    telemetry_list = []
    labels_list = []
    crops = ["Corn", "Wheat", "Soybeans", "Cotton"]
    
    for i in range(n_tractors):
        t_id = f"T-{i:03d}"
        profile = profiles[i]
        
        if profile == 'Healthy':
            v_mu, v_sigma, h_mu, h_sigma = 8.0, 1.0, 65.0, 3.0
            fail_label = 0
        elif profile == 'Degrading':
            v_mu, v_sigma, h_mu, h_sigma = 11.5, 1.5, 75.0, 5.0
            fail_label = 1 if np.random.random() > 0.4 else 0
        else:
            v_mu, v_sigma, h_mu, h_sigma = 14.5, 2.0, 85.0, 6.0
            fail_label = 1
            
        vibs = np.random.normal(v_mu, v_sigma, days)
        heats = np.random.normal(h_mu, h_sigma, days)
        pressures = np.random.normal(50, 8, days)
        
        errors = np.random.choice(3, size=days, p=[0.94, 0.04, 0.02])
        
        for d in range(days):
            telemetry_list.append({
                "tractor_id": t_id,
                "day": d + 1,
                "vibration_index": round(vibs[d], 2),
                "heat_index": round(heats[d], 2),
                "oil_pressure": round(pressures[d], 2),
                "sensor_error_code": int(errors[d])
            })
            
        labels_list.append({
            "tractor_id": t_id,
            "crop_type": np.random.choice(crops),
            "failure_target": fail_label
        })

    pd.DataFrame(telemetry_list).to_csv("telemetry_raw.csv", index=False)
    pd.DataFrame(labels_list).to_csv("maintenance_registry.csv", index=False)
    print("Success: 'telemetry_raw.csv' and 'maintenance_registry.csv' created.")

if __name__ == "__main__":
    generate_assignment_data()