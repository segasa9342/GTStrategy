import PySimpleGUI as sg
import datetime
import pandas as pd

pd.set_option("display.max_rows", None, "display.max_columns", None)

percent = lambda part, whole: float(whole) / 100 * float(part)


def get_sec(time_str):
    # Trasforma minuti in secondi
    h, m, s, t = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s) + 0.001 * int(t)


def distribute(oranges, plates):
    base, extra = divmod(oranges, plates)  # extra < plates
    if extra == 0:
        L = [base for _ in range(plates)]
    elif extra <= plates // 2:
        leap = plates // extra
        L = [base + (i % leap == leap // 2) for i in range(plates)]
    else:  # plates/2 < extra < plates
        leap = plates // (plates - extra)  # plates - extra is the number of apples I lent you
        L = [base + (1 - (i % leap == leap // 2)) for i in range(plates)]
    return L


def initialise():
    sg.theme('Tan Blue')
    layout = [
        [sg.Image(r'/Users/salvo/Desktop/GT Sport/LogoSI.png')],
        [sg.Text('GT Sport Pit Strategy Calculator', size=(35, 1), justification='center', font=("Helvetica", 25))],
        [sg.Frame(layout=[
            [sg.Text('Total Race Laps'), sg.InputText('30', key="TotalLapNumber", size=(8, 10), justification='Right')],
            [sg.Text('Circuit'),
             sg.InputOptionMenu(('Menu Option 1', 'Menu Option 2', 'Menu Option 3'), key='Circuit')],
            [sg.Text('Pit Lane Time (in hh:mm:ss)'), sg.InputText('00:00:00:000', key="PitLaneTime", size=(10, 1))],
            [sg.Text('Initial Fuel Level'), sg.InputText('50', key="InitialFuelRace", size=(8, 1), justification='Right')],
            [sg.Text('Predicted number of Pit Stops'), sg.InputText('', key="PredictedPitStop", size=(8, 1), justification='Right')]
        ],
            title='Race Information', title_color='red', relief=sg.RELIEF_SUNKEN),
            sg.Frame(layout=[
                [sg.Text('Number of Test Laps'), sg.InputText('10', key="TestLaps", size=(8, 1), justification='Right')],
                [sg.Text('Total Time (in hh:mm:ss:000)'), sg.InputText('00:11:25:420', key="TestTime", size=(10, 1), justification='Right')],
                [sg.Text('Initial Fuel Level (in litres)'), sg.InputText('100', key="InitialFuelTest", size=(8, 1), justification='Right')],
                [sg.Text('Final Fuel Level (in litres)'), sg.InputText('5', key="FinalFuelTest", size=(8, 1), justification='Right')],

            ],
                title='Test Information', title_color='red', relief=sg.RELIEF_SUNKEN)],
        [sg.Text('Tyre Wear'), sg.Text('Lowest'),
         sg.Slider(range=(0, 10), orientation='h', size=(34, 20), default_value=2, key="TyreWear"), sg.Text('Lowest')],
        [sg.Text('Fuel Consumption'), sg.Text('Lowest'),
         sg.Slider(range=(0, 30), orientation='h', size=(34, 20), default_value=3, key="FuelConsumption"),
         sg.Text('Highest')],
        # [sg.Text('Strategy Balance'), sg.Slider(range=(1, 100), orientation='h', size=(34, 20), default_value=50, key="Strategy Balance")],

        [sg.Submit(tooltip='Calcola'), sg.Cancel()],
    ]

    window = sg.Window('GT Sport Pit Strategy Calculator', layout, default_element_size=(40, 1), grab_anywhere=False)
    while True:
        event, initialise.values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        if event == 'Submit':
            calculate()



def calculate():
    global TotalLapNumber
    TotalLapNumber = int(initialise.values["TotalLapNumber"])
    InitialFuel = int(initialise.values["InitialFuelTest"])
    FinalFuel = int(initialise.values["FinalFuelTest"])
    InitialFuelRace = int(initialise.values["InitialFuelRace"])
    if initialise.values["PredictedPitStop"] is not "":
        UserInputPitStop = int(initialise.values["FuelConsumption"])
    FuelBaseLine = 100
    EngineMode = 1

    if int(initialise.values["TyreWear"]) == 0:
        if int(initialise.values["TyreWear"]) == 0:
            sg.popup_error('You need no strategy! Just Push!')
            initialise()

    # Display a progress meter. Allow user to break out of loop using cancel button
    for i in range(10):
        if not sg.OneLineProgressMeter('My 1-line progress meter', i + 1, 10, 'single'):
            break
    ####
    #### MOLTIPLICATORI CARBURANTE E GOMME // FUEL AND TYRE MULTIPLIERS
    ####
    FuelMultiplier = 0.01 * initialise.values[
        "FuelConsumption"]  ### Coefficiente miglioramento prestazione dovuto al consumo di carburante
    TyreWearMultiplier = 0.01 * initialise.values[
        "TyreWear"]  ### Coefficiente peggioramento prestazione dovuto al consumo di gomme

    ####
    #### PASSO GARA TEST = Tempo totale / Giri effettuati // RACE PACE
    ####
    try:
        RacePaceSeconds = float(get_sec(initialise.values["TestTime"])) / int((initialise.values["TestLaps"]))
        RacePaceMinutes = datetime.timedelta(seconds=RacePaceSeconds)
        print("Average Lap Pace: ", str(RacePaceMinutes))
    except ZeroDivisionError:
        sg.popup_error('Invalid input data!')
        initialise()
    except ValueError:
        sg.popup_error('Invalid input data!')
        initialise()
    ####
    #### CONSUMO CARBURANTE PER GIRO = (Carburante iniziale test - Carburante final test) / Giri test effettuati || FUEL CONSUMPTION PER LAP
    ####
    try:
        ConsumedFuelPerLap = ((InitialFuel - FinalFuel) / int(initialise.values["TestLaps"])) * EngineMode
        print("Fuel Per Lap: ", ConsumedFuelPerLap, "litres")
    except ValueError:
        sg.popup_error('Invalid input data!')
        initialise()
    ####
    #### CARBURANTE NECESSARIO PER TUTTA LA GARA // FUEL NEEDED FOR THE WHOLE RACE
    ####
    try:
        FuelNeeded = (int(ConsumedFuelPerLap)) * TotalLapNumber
        print("Fuel Needed to Finish the Race: ", FuelNeeded, "litres")
    except ValueError:
        sg.popup_error('Invalid input data!')
        initialise()
    ####
    #### COSTANTE USURA CARBURANTE (k)
    ####
    try:
        k = RacePaceMinutes.total_seconds() / ((InitialFuel - FinalFuel) / 2)
        # print("Coefficente k=", k)
    except ValueError:
        sg.popup_error('Invalid input data!')
        initialise()
    ###
    ### CALCOLO LUNGHEZZA STINT / STINT LENGHT CALCULATOR
    ###
    FirstStint = int(InitialFuelRace / ConsumedFuelPerLap)
    try:
        if initialise.values["PredictedPitStop"] is not "":
            if initialise.values["PredictedPitStop"] is not 1:
                PitLaps = distribute(oranges=(TotalLapNumber - FirstStint),
                                     plates=int(initialise.values["PredictedPitStop"]))
            else:
                PitLaps = [FirstStint]
        else:
            PitLaps = distribute(oranges=(TotalLapNumber - FirstStint),
                                 plates=int((FuelNeeded - (FirstStint * ConsumedFuelPerLap)) // FuelBaseLine))
            StintLenght = int((TotalLapNumber - FirstStint) / len(PitLaps))
            FuelPerStint = StintLenght * ConsumedFuelPerLap
            while FuelPerStint > 100:
                FuelBaseLine = FuelBaseLine - 1
                PitLaps = distribute(oranges=(TotalLapNumber - FirstStint),
                                     plates=int((FuelNeeded - (FirstStint * ConsumedFuelPerLap)) // FuelBaseLine))
                StintLenght = int((TotalLapNumber - FirstStint) / len(PitLaps))
                FuelPerStint = StintLenght * ConsumedFuelPerLap

        PredictedStops = len(PitLaps)
        StintLenght = int((TotalLapNumber - FirstStint) / int(PredictedStops))
        FuelPerStint = StintLenght * ConsumedFuelPerLap

        ConsolidatedPitLaps = [FirstStint]

        for i in range(len(PitLaps)):
            PitLap = ConsolidatedPitLaps[i] + StintLenght
            ConsolidatedPitLaps.append(PitLap)

        print("We have", int(StintLenght), "laps per stint, for a total of", int(PredictedStops), "stops")
        print("You are pitting on laps", ConsolidatedPitLaps)
        print("For each stint, you will burn", FuelPerStint, "litres")

    except ValueError:
        sg.popup_error('Invalid input data!')
        initialise()
    ###
    ### CREAZIONE DATAFRAME
    ###
    global LapChart
    LapChart = pd.DataFrame(
        columns=["LapNumber", "PredictedTimeMin", "PredictedTimeMax", "EngineMode", "FuelRemaining", "TyreWear", "Pit",
                 "PitLaneTime", "FuelAdded", "TyreChange"])
    for i in range(1, TotalLapNumber + 1):
        CurrentLap = i
        LapChart.loc[CurrentLap, 'LapNumber'] = CurrentLap
        LapChart.loc[CurrentLap, 'EngineMode'] = EngineMode

        ### Fuel Remaining
        if CurrentLap == 1:
            LapChart.loc[CurrentLap, 'Pit'] = "-"
            LapChart.loc[CurrentLap, 'PitLaneTime'] = "-"
            LapChart.loc[CurrentLap, 'PitLaneTime'] = "-"
            LapChart.loc[CurrentLap, 'FuelAdded'] = "-"
            LapChart.loc[CurrentLap, 'TyreChange'] = "-"
            FuelRemaining = InitialFuelRace
        elif CurrentLap in ConsolidatedPitLaps:
            LapChart.loc[CurrentLap, 'Pit'] = "YES"
            FuelRemaining = FuelPerStint
            if TotalLapNumber - CurrentLap < StintLenght:
                FuelRemaining = (TotalLapNumber - CurrentLap) * ConsumedFuelPerLap
            LapChart.loc[CurrentLap, 'FuelAdded'] = (FuelPerStint - FuelRemaining)
        else:
            LapChart.loc[CurrentLap, 'Pit'] = "-"
            LapChart.loc[CurrentLap, 'PitLaneTime'] = "-"
            LapChart.loc[CurrentLap, 'PitLaneTime'] = "-"
            LapChart.loc[CurrentLap, 'FuelAdded'] = "-"
            LapChart.loc[CurrentLap, 'TyreChange'] = "-"
            FuelRemaining = FuelRemaining - ConsumedFuelPerLap
        LapChart.loc[CurrentLap, 'FuelRemaining'] = FuelRemaining

        ### Passo gara stimato carburante
        FuelTimeBaseline = (RacePaceSeconds + (k * FuelRemaining * FuelMultiplier))

        LapChart.loc[CurrentLap, 'PredictedTimeMin'] = datetime.timedelta(
            seconds=FuelTimeBaseline - percent(1, FuelTimeBaseline))
        LapChart.loc[CurrentLap, 'PredictedTimeMax'] = datetime.timedelta(
            seconds=FuelTimeBaseline + percent(1., FuelTimeBaseline))

    print(LapChart)

    print("_______________________________________")
    output()


def output():
    sg.theme('Tan Blue')

    # ------ Make the Table Data ------

    columm_layout =  [
                [sg.Text(LapChart.iloc[i,0],  size=(3, 1), justification='right', key="_LAPNUMBER_")] +
                [sg.Text(LapChart.iloc[i,1],  size=(15, 1), justification='right', key="_MINLAPTIME_")] +
                [sg.Text(LapChart.iloc[i,2], size=(15, 1), justification='right', key="_MAXLAPTIME")] +
                [sg.InputOptionMenu(values=[j for j in range(1,7)], default_value=LapChart.iloc[i,3], size=(15, 4), key='_ENGINEMODE')] +
                [sg.Spin([j for j in range(1,100)], initial_value=float(LapChart.iloc[i,4]), size=(4,1), key="_FUELREMAINING", change_submits=True)] +
                [sg.Text(LapChart.iloc[i,5], size=(4, 1), justification='right', key="_TYREWEAR")] +
                [sg.InputOptionMenu(values=("-","YES"), default_value=LapChart.iloc[i,6], size=(15, 4), key='_PITMENU_')] +
                [sg.Text(LapChart.iloc[i, 7], size=(15, 1), justification='right', key="_PITLANETIME_")] +
                [sg.Text(LapChart.iloc[i,8], size=(15, 1), justification='right', key="_FUELADDED_")] +
                [sg.InputOptionMenu(values=("-", "YES"), default_value=LapChart.iloc[i, 9], size=(15, 4), key='_PITMENU_')]

        for i in range(TotalLapNumber)]

    # ------ Window Layout ------
    layout = [
        [sg.Image(r'/Users/salvo/Desktop/GT Sport/LogoSI.png')],
        [sg.Text('GT Sport Pit Strategy Calculator', size=(35, 1), justification='center', font=("Helvetica", 25))],
        [sg.Col(columm_layout, scrollable=True)],
        [sg.Frame(layout=[
            [sg.Text('Total Race Time')],
        ],
            title='Race Information', title_color='red', relief=sg.RELIEF_SUNKEN)],

        [sg.Button('Calculate'), sg.Button('Exit')],

        ]
    # ------ Create Window ------
    window = sg.Window('The Table Element', layout,
                        font='Courier 13',
                       location=(0, 0)
                       )

    # ------ Event Loop ------
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            break

    window.close()


initialise()
