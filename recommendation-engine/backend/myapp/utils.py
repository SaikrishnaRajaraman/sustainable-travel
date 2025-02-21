# This is the account for emissions during takeoff and landing
def get_gcd_correction(miles):
    kms = miles_to_kms(miles)
    if kms < 550:
        kms += 50
    elif kms > 550 and kms < 5500:
        kms += 100
    elif kms > 5500:
        kms += 125

    return kms_to_miles(kms)


def kms_to_miles(kms):
    return kms * 0.621371



def calculate_carbon_emission(miles):
    # For 1 passenger-mile travelled, 0.160308027 kgs of CO2 is emitted(kg)
    #emission = Miles*Emission/passenger-mile
    #GCD Correction
    kms = miles_to_kms(miles)
    fuel = calculate_fuel(kms)
    #Average P/C = 82.53
    #2024 Load Factor = 83.39
    # Formula = CO2 emmissions = Fuel * (Passenger/Cargo Ratio / Total occupied seats) * Total Seats * 3.16
    return fuel * (82.53/83.39) * 100 * 3.16

def miles_to_kms(miles):
    kms = miles * 1.60934
    return kms

def calculate_fuel(distance):
    distances = [125, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500]
    fuel_consumptions = [1683.5, 3434.5, 4550, 6132.5, 7644.5, 10535, 13306, 15994.5, 45734.5, 52412, 58824.5, 64882, 70842.5, 76714.5, 82226, 87364, 92390.5, 107440, 112934, 118340]

    if distance <= distances[0]:
        return fuel_consumptions[0]
    elif distance >= distances[-1]:
        return fuel_consumptions[-1]
    else:
        for i in range(len(distances) - 1):
            if distances[i] <= distance < distances[i+1]:
                x0, x1 = distances[i], distances[i+1]
                y0, y1 = fuel_consumptions[i], fuel_consumptions[i+1]
                return y0 + (y1 - y0) * (distance - x0) / (x1 - x0)

    return 0  # This should never happen if the input is valid


def kg_to_metric_ton(kg):
    return kg / 1000