Object subclass: #Ride
    instanceVariableNames: 'rideID pickupLocation dropoffLocation distanceInMiles fareAmount'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!Ride methodsFor: 'accessing'!
rideID: value
    rideID := value
!

pickupLocation: value
    pickupLocation := value
!

dropoffLocation: value
    dropoffLocation := value
!

distanceInMiles: value
    distanceInMiles := value
!

fareAmount: value
    fareAmount := value
!
!

!Ride methodsFor: 'fare and display'!
fare
    ^ fareAmount
!

rideDetails
    Transcript show: '  Ride ID: ', rideID; cr.
    Transcript show: '  Pickup: ', pickupLocation,
        ' -> Dropoff: ', dropoffLocation; cr.
    Transcript show: '  Distance: ', distanceInMiles printString,
        ' miles, Fare: $', self fare printString; cr
!
!

!Ride class methodsFor: 'instance creation'!
rideId: rideIdentifier pickup: pickupPlace dropoff: dropoffPlace distance: distanceMiles
    | newRide |
    newRide := self new.
    newRide
        rideID: rideIdentifier;
        pickupLocation: pickupPlace;
        dropoffLocation: dropoffPlace;
        distanceInMiles: distanceMiles;
        fareAmount: (distanceMiles * 1.5).
    ^ newRide
!
!


"========================"
" Standard Ride "
"========================"

Ride subclass: #StandardRide
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!StandardRide methodsFor: 'fare and display'!
rideDetails
    Transcript show: '  [Standard Ride]'; cr.
    super rideDetails
!
!

!StandardRide class methodsFor: 'instance creation'!
rideId: rideIdentifier pickup: pickupPlace dropoff: dropoffPlace distance: distanceMiles
    | newRide |
    newRide := self new.
    newRide
        rideID: rideIdentifier;
        pickupLocation: pickupPlace;
        dropoffLocation: dropoffPlace;
        distanceInMiles: distanceMiles;
        fareAmount: (distanceMiles * 1.75).
    ^ newRide
!
!


"========================"
" Premium Ride "
"========================"

Ride subclass: #PremiumRide
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!PremiumRide methodsFor: 'fare and display'!
rideDetails
    Transcript show: '  [Premium Ride]'; cr.
    super rideDetails
!
!

!PremiumRide class methodsFor: 'instance creation'!
rideId: rideIdentifier pickup: pickupPlace dropoff: dropoffPlace distance: distanceMiles
    | newRide |
    newRide := self new.
    newRide
        rideID: rideIdentifier;
        pickupLocation: pickupPlace;
        dropoffLocation: dropoffPlace;
        distanceInMiles: distanceMiles;
        fareAmount: (distanceMiles * 2.5).
    ^ newRide
!
!


"========================"
" Driver "
"========================"

Object subclass: #Driver
    instanceVariableNames: 'driverID driverName driverRating assignedRides'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!Driver methodsFor: 'accessing'!
driverID: value
    driverID := value
!

driverName: value
    driverName := value
!

driverRating: value
    driverRating := value
!

assignedRides: collection
    assignedRides := collection
!
!

!Driver methodsFor: 'rides'!
addRide: rideToAdd
    assignedRides add: rideToAdd
!

getDriverInfo
    Transcript show: 'Driver ID: ', driverID,
        ', Name: ', driverName,
        ', Rating: ', driverRating printString; cr.
    Transcript show: '  Completed rides: ',
        assignedRides size printString; cr.

    1 to: assignedRides size do: [:i |
        Transcript show: '  --- Ride ', i printString, ' ---'; cr.
        (assignedRides at: i) rideDetails
    ]
!
!

!Driver class methodsFor: 'instance creation'!
driverId: identifier name: nameValue rating: ratingValue
    | newDriver |
    newDriver := self new.
    newDriver
        driverID: identifier;
        driverName: nameValue;
        driverRating: ratingValue;
        assignedRides: OrderedCollection new.
    ^ newDriver
!
!


"========================"
" Rider "
"========================"

Object subclass: #Rider
    instanceVariableNames: 'riderID riderName requestedRides'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!Rider methodsFor: 'accessing'!
riderID: value
    riderID := value
!

riderName: value
    riderName := value
!

requestedRides: collection
    requestedRides := collection
!
!

!Rider methodsFor: 'rides'!
requestRide: rideToAdd
    requestedRides add: rideToAdd
!

viewRides
    Transcript show: 'Rider ID: ', riderID,
        ', Name: ', riderName; cr.
    Transcript show: '  Requested rides: ',
        requestedRides size printString; cr.

    1 to: requestedRides size do: [:i |
        Transcript show: '  --- Ride ', i printString, ' ---'; cr.
        (requestedRides at: i) rideDetails
    ]
!
!

!Rider class methodsFor: 'instance creation'!
riderId: identifier name: nameValue
    | newRider |
    newRider := self new.
    newRider
        riderID: identifier;
        riderName: nameValue;
        requestedRides: OrderedCollection new.
    ^ newRider
!
!

Object subclass: #RideSharingDemo
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: 'RideSharing'
!

!RideSharingDemo class methodsFor: 'running'!
run
    | rides driver rider |

    Transcript cr.
    Transcript show: 'Ride Sharing System - OOP Demo (Squeak)'; cr.
    Transcript show: 'Encapsulation, Inheritance, Polymorphism'; cr; cr.

    rides := OrderedCollection new.
    rides add: (StandardRide rideId: 'R001' pickup: 'Downtown' dropoff: 'Airport' distance: 12).
    rides add: (PremiumRide rideId: 'R002' pickup: 'Mall' dropoff: 'Station' distance: 5).
    rides add: (StandardRide rideId: 'R003' pickup: 'Hotel' dropoff: 'Convention Center' distance: 3.5).
    rides add: (PremiumRide rideId: 'R004' pickup: 'University' dropoff: 'Downtown' distance: 8).

    Transcript show: 'Fares:'; cr.
    rides doWithIndex: [:ride :i |
        Transcript show: '  Ride ', i printString,
            ' fare: $', ride fare printString; cr
    ].

    Transcript cr; show: 'Ride Details:'; cr.
    rides doWithIndex: [:ride :i |
        Transcript show: '--- Ride ', i printString, ' ---'; cr.
        ride rideDetails
    ].

    Transcript cr; show: 'Driver Info:'; cr.
    driver := Driver driverId: 'D01' name: 'Alice' rating: 4.8.
    driver addRide: (StandardRide rideId: 'R101' pickup: 'A St' dropoff: 'B St' distance: 4).
    driver addRide: (PremiumRide rideId: 'R102' pickup: 'C St' dropoff: 'D St' distance: 7).
    driver getDriverInfo.

    Transcript cr; show: 'Rider Info:'; cr.
    rider := Rider riderId: 'U01' name: 'Bob'.
    rider requestRide: (StandardRide rideId: 'R201' pickup: 'Home' dropoff: 'Office' distance: 6).
    rider requestRide: (PremiumRide rideId: 'R202' pickup: 'Office' dropoff: 'Airport' distance: 15).
    rider viewRides.

    Transcript cr; show: 'Done.'; cr
!
!
