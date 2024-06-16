import csv
import math
import os
from collections import defaultdict
from typing import List, Tuple, Optional, Dict

class MediaConcentrationAnalysis:
    CR3_LIMITS = [(35, 'Low Concentration'), (55, 'Moderate Concentration'), (float('inf'), 'High Concentration')]
    CR4_LIMITS = [(35, 'No Concentration'), (50, 'Low Concentration'), (65, 'Moderate Concentration'), 
                  (75, 'High Concentration'), (float('inf'), 'Very High Concentration')]
    CR8_LIMITS = [(45, 'No Concentration'), (70, 'Low Concentration'), (85, 'Moderate Concentration'), 
                  (90, 'High Concentration'), (float('inf'), 'Very High Concentration')]
    HHI_LIMITS = [(1000, 'Not Concentrated'), (1800, 'Moderately Concentrated'), (float('inf'), 'Highly Concentrated')]
    MOCDI_LIMITS = [(300, 'Not Concentrated'), (500, 'Moderately Concentrated'), (float('inf'), 'Highly Concentrated')]

    @staticmethod
    def classify(value: float, limits: List[Tuple[float, str]]) -> str:
        """
        Classify a value based on provided limits.

        :param value: Value to classify.
        :param limits: List of tuples containing limits and their corresponding classifications.
        :return: Classification as a string.
        """
        for limit, classification in limits:
            if value <= limit:
                return classification
        return 'Unknown'

    @classmethod
    def CR_CLASSIFICATION(cls, cr_value: float, cr_n: int) -> str:
        """
        Classify the Concentration Ratio (CR) value based on the number of broadcasters (cr_n).

        :param cr_value: CR value.
        :param cr_n: Number of broadcasters considered (3, 4, or 8).
        :return: Classification as a string.
        """
        if cr_n == 3:
            return cls.classify(cr_value, cls.CR3_LIMITS)
        elif cr_n == 4:
            return cls.classify(cr_value, cls.CR4_LIMITS)
        elif cr_n == 8:
            return cls.classify(cr_value, cls.CR8_LIMITS)
        return 'Unknown'

    @classmethod
    def CR_VALUE(cls, broadcasters: List[Tuple[str, float]], cr_n: int) -> float:
        """
        Calculate the CR value for the first cr_n broadcasters.

        :param broadcasters: List of tuples containing broadcasters and their percentages.
        :param cr_n: Number of broadcasters considered.
        :return: CR value.
        """
        return sum(percentage for _, percentage in broadcasters[:cr_n])

    @staticmethod
    def CR(broadcasters: List[Tuple[str, float]]) -> Optional[List[Tuple[int, float, str]]]:
        """
        Calculate CR values and their classifications for 3, 4, and 8 broadcasters.

        :param broadcasters: List of tuples containing broadcasters and their percentages.
        :return: List of tuples with the number of broadcasters, CR value, and classification, or None if fewer than 3 broadcasters.
        """
        qtd_broadcasters = len(broadcasters)
        if qtd_broadcasters < 3:
            return None

        cr_values = []
        for cr_n in (3, 4, 8):
            if cr_n <= qtd_broadcasters:
                cr_value = MediaConcentrationAnalysis.CR_VALUE(broadcasters, cr_n)
                cr_values.append((cr_n, cr_value, MediaConcentrationAnalysis.CR_CLASSIFICATION(cr_value, cr_n)))

        return cr_values

    @classmethod
    def HHI_CLASSIFICATION(cls, hhi_value: float) -> str:
        """
        Classify the Herfindahl-Hirschman Index (HHI) value.

        :param hhi_value: HHI value.
        :return: Classification as a string.
        """
        return cls.classify(hhi_value, cls.HHI_LIMITS)

    @staticmethod
    def HHI(broadcasters: List[Tuple[str, float]]) -> Tuple[float, str]:
        """
        Calculate the HHI value and its classification.

        :param broadcasters: List of tuples containing broadcasters and their percentages.
        :return: Tuple with HHI value and classification.
        """
        hhi_value = sum(percentage ** 2 for _, percentage in broadcasters)
        return hhi_value, MediaConcentrationAnalysis.HHI_CLASSIFICATION(hhi_value)

    @classmethod
    def MOCDI_CLASSIFICATION(cls, mocdi_value: float) -> str:
        """
        Classify the Market Concentration Index (MOCDI) value.

        :param mocdi_value: MOCDI value.
        :return: Classification as a string.
        """
        return cls.classify(mocdi_value, cls.MOCDI_LIMITS)

    @staticmethod
    def MOCDI(broadcasters: List[Tuple[str, float]], hhi_value: Optional[float] = None) -> Tuple[float, str]:
        """
        Calculate the MOCDI value and its classification.

        :param broadcasters: List of tuples containing broadcasters and their percentages.
        :param hhi_value: HHI value, if already calculated. If None, it will be calculated.
        :return: Tuple with MOCDI value and classification.
        """
        if hhi_value is None:
            hhi_value, _ = MediaConcentrationAnalysis.HHI(broadcasters)
        mocdi_value = hhi_value / math.sqrt(len(broadcasters))
        return mocdi_value, MediaConcentrationAnalysis.MOCDI_CLASSIFICATION(mocdi_value)

    @staticmethod
    def HI(broadcasters: List[Tuple[str, float]]) -> float:
        """
        Calculate the Hirschman Index (HI).

        :param broadcasters: List of tuples containing broadcasters and their percentages.
        :return: HI value.
        """
        return sum(math.sqrt(percentage) for _, percentage in broadcasters)

    @staticmethod
    def read_input_file() -> Optional[Dict[str, List[Tuple[str, float]]]]:
        """
        Read the data from the input file (input.csv or input.txt) and return a dictionary with broadcasters by location.

        :return: Dictionary with locations as keys and lists of tuples (broadcaster, percentage) as values.
        """
        input_file = None
        for file_name in ('input.csv', 'input.txt'):
            if os.path.isfile(file_name):
                input_file = file_name
                break

        if input_file is None:
            print("Input file not found. Make sure there is an 'input.csv' or 'input.txt' file.")
            return None

        locations = defaultdict(list)
        try:
            with open(input_file) as file:
                reader = csv.reader(file)
                for row in reader:
                    try:
                        local, broadcaster, percentage = row
                        if local.lower() == 'local' or percentage.lower() == 'no data':
                            continue
                        locations[local.upper()].append([broadcaster, float(percentage)])
                    except ValueError:
                        print(f"Error processing row: {row}. Skipping.")
        except (IOError, csv.Error) as e:
            print(f"Error reading the input file: {e}")
            return None

        for local in locations:
            locations[local] = sorted(locations[local], key=lambda x: x[1], reverse=True)

        print(locations)
        return locations

    @staticmethod
    def write_output(locations: Dict[str, List[Tuple[str, float]]]):
        """
        Write the analysis results to an output file (output.txt).

        :param locations: Dictionary with locations as keys and lists of tuples (broadcaster, percentage) as values.
        """
        try:
            with open('output.txt', 'w', newline='') as file:
                for local, values in locations.items():
                    cr_info = MediaConcentrationAnalysis.CR(values)
                    hhi_value, hhi_classification = MediaConcentrationAnalysis.HHI(values)
                    mocdi_value, mocdi_classification = MediaConcentrationAnalysis.MOCDI(values, hhi_value)
                    hi_value = MediaConcentrationAnalysis.HI(values)

                    file.write(f'{local}\n')
                    print(f'{local}')
                    if cr_info:
                        for cr_n, cr_value, cr_classification in cr_info:
                            file.write(f'    CR{cr_n}: {cr_value:.2f} - {cr_classification}\n')
                            print(f'    CR{cr_n}: {cr_value:.2f} - {cr_classification}')
                    file.write(f'    HHI: {hhi_value:.2f} - {hhi_classification}\n')
                    print(f'    HHI: {hhi_value:.2f} - {hhi_classification}')
                    file.write(f'    MOCDI: {mocdi_value:.2f} - {mocdi_classification}\n')
                    print(f'    MOCDI: {mocdi_value:.2f} - {mocdi_classification}')
                    file.write(f'    HI: {hi_value:.2f}\n')
                    print(f'    HI: {hi_value:.2f}')
        except IOError as e:
            print(f"Error writing the output file: {e}")

if __name__ == "__main__":
    locations = MediaConcentrationAnalysis.read_input_file()
    if locations:
        MediaConcentrationAnalysis.write_output(locations)