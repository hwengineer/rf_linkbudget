from scipy import constants
import numpy as np
import unittest

# ============================================================================ #


class RFMath:
    """
    Calculation Class for all the different Parameters

    Note
    ----
    search in this class for calculation errors
    """

    T0 = np.float(290)
    """
    numpy.float : Noisetemperature at N0
    """
    N0 = np.float(10*np.log10(constants.k * 290 * 1 * 1000))
    """
    numpy.float : Noisefloor at 25°C and 50R
    """

    defaults = {'P1': None, 'IP3': None, 'Tn': 0, 'Gain': 0}
    """
    dict : Sane default values for result dictionary
    """

    def convert_T_n(T, B=1):
        """
        Convert Noise Temperature to Noise Power

        Parameters
        ----------
        T : float
            Noise Temperature in [°K]

        Returns
        -------
        n : numpy.float
            noise power in [dBm/Hz] / [dBm/(B*Hz)]
        """
        return 10*np.log10(constants.k * T * B * 1000) if T != 0 else -np.inf

    def convert_T_NF(T, Gain):
        """
        Convert Noise Temperature to NoiseFigure

        Parameters
        ----------
        T : float
            Noise Temperature in [°K]

        Gain : float
            Accumulated Gain in [dB]

        Returns
        -------
        NF : numpy.float
            Noisefigure in [dB]

        Notes
        -----
        .. _Wiki: https://en.wikipedia.org/wiki/Noise_temperature
        """
        g = 10**(Gain/10)
        Teq = T/g
        F = Teq/RFMath.T0

        return 10*np.log10(F)

    def calc_IM3(P, IP3):
        """
        Calculate Intermodulation Value IM3 (absolute)
        from P and IP3

        Parameters
        ----------
        P : float
            Signal ower in [dBm]
        IP3 : float
            IP3 in [dBm]

        Returns
        -------
        IM3 : float or None
            intermodulation 3 power in [dBm]
        """
        return P - (2*(IP3 - P) + 6) if(IP3 is not None) else None

    def calc_IMD3(P, IP3):
        """
        Calculate Intermodulation 3 distance between P and IM3
        from P and IP3

        Parameters
        ----------
        P : float
            Signal ower in [dBm]
        IP3 : float
            IP3 in [dBm]

        Returns
        -------
        IMD3 : float or None
            distance between signal power and intermodulation power in [dBm]
        """
        return 2*(IP3 - P) + 6 if(IP3 is not None) else None

    def calc_SNR(P, n):
        """
        Calculate SNR value
        from P and n

        Parameters
        ----------
        P : float
            Signal power in [dBm]
        n : float
            Noise power in [dBm/Hz]

        Returns
        -------
        SNR : float
            distance between Signal and Noise power in [dB]
        """
        return P - n

    def calc_SFDR(P, IM3):
        """
        Calculate SFDR value
        from P and IM3

        Parameters
        ----------
        P : float
            Signal power in [dBm]
        IM3 : float
            Intermodulation 3 power in [dBm]

        Returns
        -------
        SFDR : float or None
            Spurious free dynamic range in [dB]
        """
        return P - IM3 if(IM3 is not None) else None

    def calc_Dynamic(SNR, SFDR):
        """
        Calculate Dynamic value
        from SNR and SFDR

        Parameters
        ----------
        SNR : float
            Signal to Noise ratio in [dB]
        SFDR : float
            Spurious free dynamic range in [dB]

        Returns
        -------
        Dynamic : int
            Dynamic, min(SNR, SFDR) in [dB]
        """
        return min(SNR, SFDR) if(SFDR is not None) else None

    def calc_P1(P1_in, P1, Gain):
        """
        Calculate P1 value

        Parameters
        ----------
        P1_in : float
            Compression Point 1 from predecessor stage in [dBm]
        P1: float
            Compression Point 1 in [dBm]
        Gain: float
            Gain in [dB]

        Returns
        -------
        P1 : float or None
            Output Compression Point 1 in [dBm]
        """

        v1 = P1_in + Gain if P1_in is not None else None
        v2 = P1
        return None if not any([v1, v2]) else min(filter(None, [v1, v2]))  # return None or minimum of both variables

    def calc_IP3(IP3_in, IP3, Gain):
        """
        Calculate IP3 value

        Parameters
        ----------
        IP3_in : float
            Compression Point 3 from predecessor stage in [dBm]
        IP3: float
            Compression Point 3 in [dBm]
        Gain: float
            Gain in [dB]

        Returns
        -------
        IP3 : float or None
            Output Compression Point 3 in [dBm]
        """

        v1 = IP3_in + Gain if IP3_in is not None else None
        v2 = IP3
        return None if not any([v1, v2]) else min(filter(None, [v1, v2]))  # return None or minimum of both variables

    def calc_Pout(P, Gain):
        """
        Calculate Signal output power

        Parameters
        ----------
        P : float
            Input signal power in [dBm]
        Gain: float
            Gain in [dB]

        Returns
        -------
        P : float
            Output signal power in [dBm]
        """
        return P + Gain

    def calc_Tn(Tn_in, Tn, Gain):
        """
        Calculate output noise temperature

        Parameters
        ----------
        Tn_in : float
            Input noise temperature in [°K]
        Tn : float
            Noise temperature of this stage in [°K]
        Gain: float
            Gain in [dB]

        Returns
        -------
        Tn : float
            Output noise temperature in [°K]
        """
        return 10**(Gain/10) * (Tn_in + Tn)

# ============================================================================ #


class RFMathTest(unittest.TestCase):
    def test_calc_SNR(self):
        value = RFMath.calc_SNR(10, 5)
        self.assertEqual(5, value)

        # assertEquals
        # assertTrue
        # assertFalse
        # assertRaises
    def test_calc_SFDR(self):
        value = RFMath.calc_SFDR(10, 5)
        self.assertEqual(5, value)

    def test_calc_Dynamic(self):
        value = RFMath.calc_Dynamic(10, 6)
        self.assertEqual(6, value)

    def test_calc_Dynamic2(self):
        value = RFMath.calc_Dynamic(3, 6)
        self.assertEqual(3, value)

# ============================================================================ #


if __name__ == "__main__":
    unittest.main()
