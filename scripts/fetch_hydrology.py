import cdsapi
import os

# Create directory
output_path = "C:/HUFP_SENTINEL_V6/data/hydrology"
if not os.path.exists(output_path):
    os.makedirs(output_path)

c = cdsapi.Client()

print("🛡️ Sentinel V7.0: Attempting Zero-Conflict Handshake for Lucknow...")

try:
    c.retrieve(
        'cems-glofas-historical',
        {
            # We strip the version/model tags to let the server use the stable defaults
            'variable': [
                'river_discharge',
                'soil_wetness_index_root_zone',
                'runoff_water_equivalent'
            ],
            'year': ['2019', '2020', '2021'],
            'month': ['06', '07', '08', '09'],
            'day': [
                '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'
            ],
            # North, West, South, East
            'area': [27.5, 80.0, 26.0, 82.0],
            'format': 'netcdf', # Changed from 'data_format' to 'format'
        },
        f'{output_path}/glofas_lucknow_19_21.nc')
    
    print(f"✅ HANDSHAKE ACCEPTED: Dataset is being prepared.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")