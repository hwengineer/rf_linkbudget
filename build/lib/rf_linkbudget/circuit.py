# from scipy import constants
from abc import ABCMeta, abstractmethod
import numpy as np
from collections import OrderedDict
import networkx as nx
import itertools
import types
import copy

try:
    from .rfmath import RFMath
    from .result import simResult
    from . import verify
except ImportError:
    from rfmath import RFMath
    from result import simResult
    import verify

# ============================================================================
# Circuit Elements


class Port:
    """
    Port abstracts an input or output of a device. We register a callback at a Port

    Attributes
    ----------
    parent : AbstractDevice
        parent object
    num : int
        number of the port in the component
    """

    def __init__(self, parent, num):
        """
        Port abstracts an input or output of a device. We register a callback at a Port

        Parameters
        ----------
        parent : AbstractDevice
            parent object
        num : int
            number of the port in the component
        """
        self.num = num
        self.parent = parent
        self.connected = None

    @property
    def name(self):
        """
        Name of the Port.
        Composed of the parent name and the port number
        """
        return self.parent.name + ' Port {}'.format(self.num)

    def __rshift__(self, other):
        """
        connects two ports together. Checks for loops.

        Parameters
        ----------
        self : Port
            port to connect from
        other : Port
            port to connect to

        Raises
        ------
        ValueError
            if the second parameter is not also a Port
        ValueError
            if the second parameter is from the same device : a loop
        ValueError
            if Port is already connected

        Examples
        --------
         >>> amp1['out'] >> amp2['in']
        """
        if not isinstance(other, Port):
            raise ValueError('error, peer must also be port')

        if other.parent == self.parent:
            raise ValueError('error, loopback detected, peer port must be from another device')

        if self.connected is not None:
            raise ValueError('error, port is already connected')

        if other == self:
            raise ValueError('can not be the same port')

        self.parent.net.add_weighted_edges_from([(self, other, 1)], Gain=0)
        self.connected = True
        other.connected = True

    def __repr__(self):
        return "{}".format(self.name)

    def isOpen(self):
        """
        checks if the Port is connected to another port

        Returns
        --------
        isOpen : bool
            True if the Port is connected
        """
        return self.connected is not None

    def regCallback(self, func):
        """
        Register callback function. Is used to connect an "external" callback function to the port.
        This function gets called before each simulation with the current power and frequency.
        [dBm] / [Hz]

        Parameters
        ----------
        func : function
            function which gets added to the port

        Notes
        -----
        The callback function has the parameter freq, power
        """
        self.callback_preSimulation = types.MethodType(func, self)

    def regCallback_preIteration(self, func):  # bad name... I should change it...
        """
        Register callback function. Is used to connect an "external" callback function to the port.
        This function gets called before each simulation iteration of the specific port with the current input data, input frequency and power.
        [dict] / [Hz] / [dBm].
        In contrast to the regCallback function registered, this function gets called before iterating over the device, rather than at the beginning of the simulation.

        Parameters
        ----------
        func : function
            function which gets added to the port

        Notes
        -----
        The callback function has the parameter data, freq, power
        """
        self.callback_preIteration = types.MethodType(func, self)

    def callback_preIteration(self, data, f, p):
        """
        The actual callback function
        The intention of use is to set as example the output frequency of a mixer depending on the input frequency of the device.

        Parameters
        ----------
        data : dictionary
            the input data of the port.
        f : float
            the input frequency of the port.
        power : float
            the input power of the port.
        """
        return {}

    def callback_preSimulation(self, f, p):
        """
        The actual callback function.
        The intention of use is to set as example the input power / frequency of the simulation at the beginning of the simulation

        Parameters
        ----------
        f : float
            the input frequency of the port.
        power : float
            the input power of the port.
        """

        '''callback function for monkey patching to set initial values'''
        return {}

    def _callback_preSimulation(self, f, p):
        """
        hidden callback function to initialise the data dict with usefull defaults

        Parameters
        ----------
        f : float
            the input frequency of the port.
        power : float
            the input power of the port.

        Returns
        -------
        data : dictionary
            the output data
        """
        data = self.callback_preSimulation(f, p)
        if(len(data) > 0):
            for key, value in RFMath.defaults.items():
                if key not in data:
                    data[key] = value
            data.update(AbstractDevice.calcAdditionalParameters(data))

        return data

# ============================================================================


class Circuit:
    """
    Our base of the simulation is the Circuit class.
    We populate it with devices and make connections between them.
    Afterwards we simulate the circuit.

    Parameters
    ----------
    name : str
        circuit name
    """

    current = None
    """
    Circuit : self reference for easy circuit construction
    """

    currentNet = None
    """
    Networkx : temporary callback reference for the current used network in a simulation. Only used in the function Circuit._simulate(...)
    """

    currentSimParams = None
    """
    temporary callback reference for the current used parameters in a simulation. Only used in the function Circuit._simulate(...)
    """

    def register(child):
        """
        A function to register an AbstractDevice to the currently active Circuit

        Parameters
        ----------
        child : AbstractDevice
            a device to register to current active Circuit
        """
        Circuit.current.children.add(child)

    def __init__(self, name):
        self.name = name
        self.children = set()
        self.net = None
        Circuit.current = self

    def __getitem__(self, key):
        """
        convenience function to access named children (AbstractDevice)

        Parameters
        ----------
        key : str
            key to select a child (AbstractDevice)

        Returns
        -------
        val : AbstractDevice
            the item with key as name
        """
        return next(filter(lambda e: e.name == key, self.children))

    def __iter__(self):
        """
        convenience function to iterate over children names

        Returns
        -------
        iter : iterator
            creates iterator with all children names
        """
        return map(lambda e: e.name, self.children)

    def finalise(self):
        """
        do all checks before calculation, sweeps etc...

        Returns
        -------
        net : network
            returns generated and checked network
        """
        # Port.check()
        # Subcircuit.check()
        # Circuit.check()
        self.net = self.generateNetwork()
        return self.net

    def generateNetwork(self):
        """
        generate a network from all the AbstractDevice's which are registered at the current circuit

        Returns
        -------
        net : network
            returns generated network
        """
        net = nx.MultiDiGraph()
        [net.add_nodes_from(child.net.nodes(data=True)) for child in self.children]
        # ugly but copies attribute as well...
        [net.add_edge(edge[0], edge[1], **child.net[edge[0]][edge[1]][0]) for child in self.children for edge in child.net.edges]
        return net

    def simulate(self, network, start, end, freq, power, **kwargs):
        """
        simulate network

        Parameters
        ----------
        network : Network
            key to select a child (AbstractDevice)
        start : Port or AbstractDevice
            Starting Port of analysis
        end : Port or AbstractDevice
            Ending Port of analysis
        freq : list of floats
            System Sweep Frequency
        power : list of floats
            System Sweep Power

        Returns
        -------
        sim : rf_linkbudget.simResult
              returns simulation result
        """
        if type(start) != Port:
            start = start['out']  # assume the out port
        if type(end) != Port:
            end = end['in']  # assume the in port

        net = OrderedDict([(x, OrderedDict([(y, 0) for y in power])) for x in freq])  # initialise nested OrderedDict
        data = OrderedDict([(x, OrderedDict([(y, 0) for y in power])) for x in freq])

        for f, p in itertools.product(freq, power):
            n, d = self._simulate(network, start, end, f, p)
            net[f][p] = n
            data[f][p] = d

        return simResult(network=net, data=data)

    def _simulate(self, network, start, end, freq, power):
        """
        hidden simulate function. Which does the iterateive part of the simulation

        Parameters
        ----------
        network : Network
            key to select a child (AbstractDevice)
        start : Port or AbstractDevice
            Starting Port of analysis
        end : Port or AbstractDevice
            Ending Port of analysis
        freq : float
            System Sweep Frequency
        power : float
            System Sweep Power

        Returns
        -------
        (network, data) : (networkx, dictionary)
            returns simulation result
        """
        # 1) copy network and initialize working copy
        net = network.copy()
        Circuit.currentNet = net  # make a callback reference
        Circuit.currentSimParams = {'start': start, 'end': end, 'freq': freq, 'power': power}

        # 2) get all path related classes and call _callback_preSimulation before calc path
        [p._callback_preSimulation(freq, power) for p in net.nodes if hasattr(p.parent, 'updatePath')]

        # 3) get shortest path between start and end "port"
        ports = nx.shortest_path(net, start, end, weight='weight')

        # 4) create data structure
        data = OrderedDict([(p, {}) for p in ports])

        # 5) init data structure
        for key in data:
            data[key] = key._callback_preSimulation(freq, power)

        # 6) goto all ports and calculate the next ports value
        # decide if the edge is just a wire, then copy the parameters, otherwise compute
        for (s, e) in zip(ports[:-1], ports[1:]):
            if s.parent == e.parent:
                d = copy.deepcopy(data[s])
                d.update(s.callback_preIteration(d, freq, power))
                data[e] = s.parent.calcCurrentEdge(s, e, d)
                data[e].update(AbstractDevice.calcAdditionalParameters(data[e]))
            else:
                data[e] = data[s]  # copy data from one port to another, because its a wire...

        Circuit.currentNet = None  # clear callback reference
        Circuit.currentSimParams = None
        return (network, data)

# ============================================================================
# Abstracted Classes / Interfaces


class AbstractDevice:
    """
    AbstractDecices class is the base-class of all "Devices"


    Parameters
    ----------
    name : str
        circuit name
    n_ports : int
        Port count of the device
    **kwargs : undef
        additional Variables
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, n_ports, **kwargs):
        self.name = name
        self.ports = [Port(self, num) for num in range(0, n_ports)]
        self.net = nx.MultiDiGraph()
        Circuit.register(self)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        """
        convenience function to access the ports with numbers and strings

        Parameters
        ----------
        key : str or int
            key to select a Port

        Returns
        -------
        val : Port
            the item with key as name or as number
        """
        if type(key) != int:
            return self.ports[self._portkey[key]]
        else:
            return self.ports[key]

    @abstractmethod
    def calcCurrentEdge(self, start, end, data):
        """
        Abstract Function for calculation of the output data values

        Parameters
        ----------
        start : network edge (a Port)
            starting Port for the calculation
        end : network edge (a Port)
            ending Port for the calculation
        data : dictionary
            input data

        Returns
        -------
        data : dictionary
            calculated output data
        """
        raise NotImplementedError()

    def calcAdditionalParameters(data):
        """
        | Calc additional Parameters
        | Every AbstractDevice has to calculate its basic values like power, IP3, P1dB, etc.
        | In this function all other dependend values are calculated:

            - IM3D
            - IM3
            - n
            - NF
            - SNR
            - SFDR
            - DYN

        Parameters
        ----------
        data : dictionary
            input data

        Returns
        -------
        data : dictionary
            calculated output data
        """
        data['IMD3'] = RFMath.calc_IMD3(data['p'], data['IP3'])       # calc output IMD3 (simple, no cumulative content)
        data['IM3'] = RFMath.calc_IM3(data['p'], data['IP3'])         # calc output IM3 (simple, no cumulative content)
        data['n'] = RFMath.convert_T_n(data['Tn'])                    # Noise Power at 25°C degrees 1Hz Bandwidth
        data['NF'] = RFMath.convert_T_NF(data['Tn'], data['Gain'])    # NoiseFigure
        data['SNR'] = RFMath.calc_SNR(data['p'], data['n'])           # Signal to Noise Ration
        data['SFDR'] = RFMath.calc_SFDR(data['p'], data['IM3'])       # Spurious Free Dynamic Range
        data['DYN'] = RFMath.calc_Dynamic(data['SNR'], data['SFDR'])  # Dynamic
        return data

    def interpolateIfListOfFreqValTuple(self, freq, value):
        """
        if value is of the form: [(f,val)] then interpolate, otherwise ignore this function

        Parameters
        ----------
        freq : np.float
            frequency of interest
        value : float, or [(f,val)]
            value which might get interpolated

        Returns
        -------
        data : np.float
            value or interpolated value
        """

        if type(value) != list:
            return value
        if len(value) == 0:
            raise ValueError('value does not contain any values... thats shouldn\'t happen')
        if type(value[0]) == tuple:
            # Good thats what we expect and want to interpolate
            return np.interp(freq, *zip(*value))

# ============================================================================ #


class genericOnePort(AbstractDevice):
    """
    | A "generic" one port device.

    Parameters
    ----------
    name : string
        name of the device
    """

    def __init__(self, name):
        """
        Parameters
        ----------
        name : string
            name of the device
        """

        # Todo : implement checks and conversion to numpy arrays
        super().__init__(name, 1)
        self._portkey = {'in': 0, 'out': 0}
        self.net.add_nodes_from([port for port in self.ports])
        [self.net.add_edge(self.ports[0], port, weight=0) for port in self.ports[1:]]

# ============================================================================ #


class genericTwoPort(AbstractDevice):
    """
    | A "generic" two port device.

    Parameters
    ----------
    name : str
        device name
    Gain : list of [f, Gain]
        Gain representation in [dB], frequency in [Hz]
    Tn : list of [Tn @ Port 1, Tn @ Port 2] : Tn np.float or list of [f, Tn]
        noisetemperature of object, represented at the "target" port [°K]
    P1 : list of [P1 @ Port 1, P1 @ Port 2]
        Signal Compression Point of object, represented at the "target" port in [dB]
    IP3 : list of [P3 @ Port 1, P3 @ Port 2]
        Signal Intermodulation Point 3 of object, represented at the "target" port in [dB]
    """

    def __init__(self, name, Gain, Tn, P1, IP3):
        """
        Parameters
        ----------
        name : str
            device name
        Gain : list of [f, Gain]
            Gain representation in [dB], frequency in [Hz]
        Tn : list of [Tn @ Port 1, Tn @ Port 2]
            noisetemperature of object, represented at the "target" port [°K]
        P1 : list of [P1 @ Port 1, P1 @ Port 2]
            Signal Compression Point of object, represented at the "target" port in [dB]
        IP3 : list of [P3 @ Port 1, P3 @ Port 2]
            Signal Intermodulation Point 3 of object, represented at the "target" port in [dB]
        """
        # Todo : implement checks and conversion to numpy arrays
        super().__init__(name, 2, Gain=Gain, Tn=Tn, P1=P1, IP3=IP3)
        self._portkey = {'in': 0, 'out': 1}
        self.net.add_nodes_from([port for port in self.ports])
        [self.net.add_edge(self.ports[0], port, weight=0) for port in self.ports[1:]]

    @classmethod
    def fromSParamFile(cls, name, filename, Tn, P1, IP3, patchString='S12DB'):
        """
        | classmethod to create a two port device from a Touchstone S2P file
        | only S21 is regarded

        Parameters
        ----------
        name : str
            device name
        filename : str
            S2P filename
        Tn : list of [Tn @ Port 1, Tn @ Port 2]
            noisetemperature of object, represented at the "target" port [°K]
        P1 : list of [P1 @ Port 1, P1 @ Port 2]
            Signal Compression Point of object, represented at the "target" port in [dB]
        IP3 : list of [P3 @ Port 1, P3 @ Port 2]
            Signal Intermodulation Point 3 of object, represented at the "target" port in [dB]

        Other Parameters
        ----------------
        patchString : str
            default 'S12DB'

        Returns
        -------
        cls : genericTwoPort
            object
        """
        import skrf as rf

        sparam = rf.touchstone.Touchstone(filename)
        sparam = sparam.get_sparameter_data(format='db')

        Gain = [(f, s21) for f, s21 in zip(sparam['frequency'], sparam[patchString])]

        return cls(name, Gain=Gain, Tn=Tn, P1=P1, IP3=IP3)

    def calcCurrentEdge(self, start, end, data):
        """
        | calculates the output data values of a two port device
        | only the following values have to calculated inside this function:

            - f out
            - Gain
            - Tn out
            - p out
            - OP1dB
            - OIP3

        Parameters
        ----------
        start : network edge (a Port)
            starting Port for the calculation
        end : network edge (a Port)
            ending Port for the calculation
        data : dictionary
            input data

        Returns
        -------
        data : dictionary
            calculated output data
        """
        out = dict(data)                                                 # copy input values to output (as good defaults)

        if start == self.ports[0] and end == self.ports[1]:

            # Gain = np.interp(data['f'], *zip(*self.Gain))                 # interpolate Gain value
            Gain = self.interpolateIfListOfFreqValTuple(data['f'], self.Gain)
            Tn = self.interpolateIfListOfFreqValTuple(data['f'], self.Tn[1])
            P1 = self.interpolateIfListOfFreqValTuple(data['f'], self.P1[1])
            IP3 = self.interpolateIfListOfFreqValTuple(data['f'], self.IP3[1])

            out['Gain'] = data['Gain'] + Gain                             # calc cumulative Gain
            out['Tn'] = RFMath.calc_Tn(data['Tn'], Tn, Gain)              # calc output NoiseTemperature
            out['p'] = RFMath.calc_Pout(data['p'], Gain)                  # calc output signal power
            out['P1'] = RFMath.calc_P1(data['P1'], P1, Gain)              # calc output P1dB point
            out['IP3'] = RFMath.calc_IP3(data['IP3'], IP3, Gain)          # calc output IP3 point (simple)
            # calc other values...
            return out

        else:
            raise ValueError('this should not happen')

# ============================================================================ #


class Source(genericOnePort):
    """
    | A source device.

    Parameters
    ----------
    name : string
        name of the device

    Examples
    -------
    >>> src = Source("Source")
    >>> src['out'] >> amp1['in']
    """

    def __init__(self, name):
        super().__init__(name)

# ============================================================================ #


class Sink(genericOnePort):
    """
    | A sink device.

    Parameters
    ----------
    name : string
        name of the device

    Examples
    -------
    >>> snk = Sink("Sink")
    >>> amp2['out'] >> snk['in']
    """

    def __init__(self, name):
        super().__init__(name)

# ============================================================================ #


class Amplifier(genericTwoPort):
    """
    | An amplifier device.

    Parameters
    ----------
    name : str
        device name
    Gain : list of [f, Gain]
        Gain representation in [dB], frequency in [Hz]
    NF : numpy.float
        NoiseFigure in [dB]
    OP1dB : numpy.float
        Output Signal Compression Point in [dB]
    OIP3 : numpy.float
        Output Signal Intermodulation Point 3 in [dB]
    """

    def __init__(self, name, Gain, NF, OP1dB, OIP3):
        """
        Parameters
        ----------
        name : str
            device name
        Gain : list of [f, Gain]
            Gain representation in [dB], frequency in [Hz]
        NF : numpy.float
            NoiseFigure in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point of object in [dB]
        OIP3 : numpy.float
            Output Signal Intermodulation Point 3 of object in [dB]
        """
        # Todo : implement checks and conversion to numpy arrays
        Tn = [0, 10**(NF/10) * RFMath.T0 - RFMath.T0]
        super().__init__(name, Gain=Gain, Tn=Tn, P1=[0, OP1dB], IP3=[0, OIP3])

    @classmethod
    def fromSParamFile(cls, name, filename, NF, OP1dB, OIP3, patchString='S12DB'):
        """
        | classmethod to create an amplifier device from a Touchstone S2P file
        | only S21 is regarded

        Parameters
        ----------
        name : str
            device name
        filename : str
            S2P filename
        NF : numpy.float
            NoiseFigure in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point of object in [dB]
        OIP3 : numpy.float
            Output Signal Intermodulation Point 3 of object in [dB]

        Other Parameters
        ----------------
        patchString : str
            default 'S12DB'

        Returns
        -------
        cls : genericTwoPort
            object
        """
        import skrf as rf

        sparam = rf.touchstone.Touchstone(filename)
        sparam = sparam.get_sparameter_data(format='db')

        Gain = [(f, s21) for f, s21 in zip(sparam['frequency'], sparam[patchString])]

        return cls(name, Gain=Gain, NF=NF, OP1dB=OP1dB, OIP3=OIP3)

# ============================================================================ #


class Attenuator(genericTwoPort):
    """
    | An attenuator device.

    Parameters
    ----------
    name : str
        device name
    Att : numpy.float or [numpy.float]
        Attenuation representation in [dB]
    OP1dB : numpy.float
        Output Signal Compression Point in [dB]
    IIP3 : numpy.float
        Output Signal Intermodulation Point 3 in [dB]
    """

    def __init__(self, name, Att, OP1dB=None, IIP3=None):
        """
        Parameters
        ----------
        name : str
            device name
        Att : numpy.float or [numpy.float]
            Attenuation representation in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point in [dB]
        IIP3 : numpy.float
            Input Signal Intermodulation Point 3 in [dB]
        """

        if type(Att) != int:
            _Att = Att
            Att = min(Att)

        # Todo : implement checks and conversion to numpy arrays
        OIP3 = IIP3 - Att if IIP3 is not None else None
        Tn = [0, 10**(Att/10) * RFMath.T0 - RFMath.T0]
        super().__init__(name, Gain=[(0, -Att)], Tn=Tn, P1=[0, OP1dB], IP3=[0, OIP3])
        self._Att = _Att if type(Att) != int else None
        self._IIP3 = IIP3

        for port in self.ports:
            setattr(port, 'setAttenuation', port.parent.setAttenuation)  # create port attribute and lin parent function to it

    def setAttenuation(self, Att):
        """
        | this setter is called in a callback function
        | the values gets rounded to the nearest value inside the Att parameter given in the construction of the object

        Parameters
        ----------
        Att : numpy.float
            Attenuation representation in [dB]
        """

        if len(self._Att) > 0:
            self._Att = np.array(self._Att)
            Att = self._Att[(np.abs(self._Att - Att)).argmin()]

        self.Tn = [0, 10**(Att/10) * RFMath.T0 - RFMath.T0]
        self.Gain = [(0, -Att)]

        if self._IIP3 is not None:
            self.IP3 = [0, self._IIP3 - Att]

# ============================================================================ #


class Filter(genericTwoPort):
    """
    | A filter device.

    Parameters
    ----------
    name : str
        device name
    Att : list of (f, Att)
        Attenuation representation in [dB]
    """

    def __init__(self, name, Att, OP1dB=None):
        """
        Parameters
        ----------
        name : str
            device name
        Att : list of (f, Att)
            Attenuation representation in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point in [dB]
        """

        if not verify.VerifyParameterNumListOfTuples.verify(Att):
            raise ValueError('Parameter Att must be in the form [(freq, att), (freq, att)...]')
        if OP1dB:
            if verify.VerifyParameterNumListSingleEntry.verify(OP1dB):
                OP1dB = OP1dB[0]
            if not verify.VerifyParameterNumSingleValue.verify(OP1dB):
                raise ValueError('Parameter OP1dB must be in the form: val or [val]')

        Tn = [(f, 10**(att/10) * RFMath.T0 - RFMath.T0) for f, att in Att]
        Gain = [(f, -att) for f, att in Att]
        super().__init__(name, Gain=Gain, Tn=[0, Tn], P1=[0, OP1dB], IP3=[0, None])

    @classmethod
    def fromSParamFile(cls, name, filename, OP1dB=None, patchString='S12DB'):
        """
        | classmethod to create a filter device from a Touchstone S2P file
        | only S21 is regarded

        Parameters
        ----------
        name : str
            device name
        filename : str
            S2P filename
        OP1dB : numpy.float
            Output Signal Compression Point of object in [dB]

        Other Parameters
        ----------------
        patchString : str
            default 'S12DB'

        Returns
        -------
        cls : genericTwoPort
            object
        """
        import skrf as rf

        sparam = rf.touchstone.Touchstone(filename)
        sparam = sparam.get_sparameter_data(format='db')

        Att = [(f, -s21) for f, s21 in zip(sparam['frequency'], sparam[patchString])]

        return cls(name, Att=Att, OP1dB=OP1dB)


# ============================================================================ #


class SPDT(AbstractDevice):
    """
    | An spdt device.

    Parameters
    ----------
    name : str
        device name
    Att : numpy.float
        Attenuation representation in [dB]
    OP1dB : numpy.float
        Output Signal Compression Point in [dB]
    OIP3 : numpy.float
        Output Signal Intermodulation Point 3 in [dB]
    Iso : numpy.float
        Attenuation in case of "isolation" [dB]
    """

    def __init__(self, name, Att, OP1dB=None, OIP3=None, Iso=999):
        """
        Parameters
        ----------
        name : str
            device name
        Att : numpy.float
            Attenuation representation in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point in [dB]
        OIP3 : numpy.float
            Output Signal Intermodulation Point 3 in [dB]
        Iso : numpy.float
            Attenuation in case of "isolation" [dB]
        """
        Tn = [0, 10**(Att/10) * RFMath.T0 - RFMath.T0]

        super().__init__(name, 3, Gain=[(0, -Att)], Tn=Tn, P1=[0, OP1dB, OP1dB], IP3=[0, OIP3, OIP3], Iso=Iso)
        self._portkey = {'S': 0, 'S-1': 1, 'S-2': 2}
        self.net.add_nodes_from([port for port in self.ports])
        [self.net.add_edge(self.ports[0], port, weight=0) for port in self.ports[1:]]
        [self.net.add_edge(port, self.ports[0], weight=0) for port in self.ports[1:]]
        self.setDirection(ref=self.net)

        for port in self.ports:
            setattr(port, 'setDirection', port.parent.setDirection)  # create port attribute and lin parent function to

        self.updatePath = True  # signals that this class has a function which is path dependend!

    def setDirection(self, dir=1, ref=None):
        """
        | gets called in pre-Simulation callback function.

        Parameters
        ----------
        name : str
            device name
        Att : numpy.float
            Attenuation representation in [dB]
        OP1dB : numpy.float
            Output Signal Compression Point in [dB]
        OIP3 : numpy.float
            Output Signal Intermodulation Point 3 in [dB]

        Notes
        -----
        | The implementation is a bit of a quirk.
        | we need a reference to the current net, which was implemented by **Circuit.currentNet**
        | but we need to delete the reference at the end of the simulation.
        | (end of **Circuit._simulate()** )

        | The switch has 3 Ports :

            - 'S'
            - 'S-1'
            - 'S-2'

        | The Ports can be used in any direction.

        Examples
        --------
        >>> sw1 = SPDT('switch 1')
        >>> src['out'] >> sw1['S']
        >>> sw1['S-1'] >> amp1['in']
        >>> sw1['S-2'] >> amp2['in']
        """
        dir = self._portkey[dir] if type(dir) != int else dir
        ref = Circuit.currentNet if ref is None else ref

        if dir == 1:
            ref.add_edge(self.ports[0], self.ports[1], key=0, weight=1)
            ref.add_edge(self.ports[1], self.ports[0], key=0, weight=1)
            ref.add_edge(self.ports[0], self.ports[2], key=0, weight=10)
            ref.add_edge(self.ports[2], self.ports[0], key=0, weight=10)
        elif dir == 2:
            ref.add_edge(self.ports[0], self.ports[1], key=0, weight=10)
            ref.add_edge(self.ports[1], self.ports[0], key=0, weight=10)
            ref.add_edge(self.ports[0], self.ports[2], key=0, weight=1)
            ref.add_edge(self.ports[2], self.ports[0], key=0, weight=1)
        else:
            raise ValueError()

    def calcCurrentEdge(self, start, end, data):
        """
        | calculates the output data values of an spdt device
        | only the following values have to calculated inside this function:

            - f out
            - Gain
            - Tn out
            - p out
            - OP1dB
            - OIP3

        Parameters
        ----------
        start : network edge (a Port)
            starting Port for the calculation
        end : network edge (a Port)
            ending Port for the calculation
        data : dictionary
            input data

        Returns
        -------
        data : dictionary
            calculated output data
        """
        out = dict(data)                                              # copy input values to output (as good defaults)

        if Circuit.currentNet.get_edge_data(start, end)[0]['weight'] > 1:
            # here we have the case with a switch in isolation state
            iso = self.interpolateIfListOfFreqValTuple(data['f'], self.Iso)
            Gain = -iso
        else:
            Gain = self.interpolateIfListOfFreqValTuple(data['f'], self.Gain)  # interpolate Gain value

        out['Gain'] = data['Gain'] + Gain                             # calc cumulative Gain
        out['Tn'] = RFMath.calc_Tn(data['Tn'], self.Tn[1], Gain)      # calc output NoiseTemperature
        out['p'] = RFMath.calc_Pout(data['p'], Gain)                  # calc output signal power
        out['P1'] = RFMath.calc_P1(data['P1'], self.P1[1], Gain)      # calc output P1dB point
        out['IP3'] = RFMath.calc_IP3(data['IP3'], self.IP3[1], Gain)  # calc output IP3 point (simple)
        # calc other values...
        return out

# ============================================================================ #


class Mixer(genericTwoPort):
    """
    | A Mixer device.

    Parameters
    ----------
    name : str
        device name
    Gain : list of [f, Gain]
            Gain representation in [dB], frequency in [Hz]
    OP1dB : numpy.float
        Output Signal Compression Point in [dB]
    OIP3 : numpy.float
        Output Signal Intermodulation Point 3 in [dB]

    Notes
    -----
    use callback_preIteration, to calc output frequency {'f': ...} the rest identical to a two port object

    Warnings
    --------
    not tested well at the moment
    """

    def __init__(self, name, Gain, OP1dB, OIP3, Tn=None):
        """
        Parameters
        ----------
        name : str
            device name
        Gain : list of [f, Gain]
                Gain representation in [dB], frequency in [Hz]
        OP1dB : numpy.float
            Output Signal Compression Point in [dB]
        OIP3 : numpy.float
            Output Signal Intermodulation Point 3 in [dB]

        Notes
        -----
        use callback_preIteration, to calc output frequency {'f': ...} the rest identical to a two port object
        """
        # Todo : implement checks and conversion to numpy arrays
        Tn = [(f, 10**(-g/10) * RFMath.T0 - RFMath.T0) for f, g in Gain] if Tn is None else Tn
        super().__init__(name, Gain=Gain, Tn=Tn, P1=[0, OP1dB], IP3=[0, OIP3])

    def calcCurrentEdge(self, start, end, data):
        """
        | calculates the output data values of an spdt device
        | only the following values have to calculated inside this function:

            - f out
            - Gain
            - Tn out
            - p out
            - OP1dB
            - OIP3

        Parameters
        ----------
        start : network edge (a Port)
            starting Port for the calculation
        end : network edge (a Port)
            ending Port for the calculation
        data : dictionary
            input data

        Returns
        -------
        data : dictionary
            calculated output data
        """
        out = dict(data)                                              # copy input values to output (as good defaults)

        freq = data['f'] if 'f_ref' not in data else data['f_ref']

        Gain = np.interp(freq, *zip(*self.Gain))                 # interpolate Gain value
        Tn = np.interp(freq, *zip(*self.Tn))                     # interpolate Gain value

        out['Gain'] = data['Gain'] + Gain                             # calc cumulative Gain
        out['Tn'] = RFMath.calc_Tn(data['Tn'], Tn, Gain)              # calc output NoiseTemperature
        out['p'] = RFMath.calc_Pout(data['p'], Gain)                  # calc output signal power
        out['P1'] = RFMath.calc_P1(data['P1'], self.P1[1], Gain)      # calc output P1dB point
        out['IP3'] = RFMath.calc_IP3(data['IP3'], self.IP3[1], Gain)  # calc output IP3 point (simple)
        # calc other values...
        return out

# ============================================================================ #

# TODO: ADC class

# ============================================================================ #


if __name__ == "__main__":

    pass
