#include <iostream>
#include <memory>
#include <string>
#include <vector>

namespace
{
const double baseFareRatePerMile = 1.50;
const double standardFareRatePerMile = 1.75;
const double premiumFareRatePerMile = 2.50;
}

class Ride
{
protected:
    std::string rideID;
    std::string pickupLocation;
    std::string dropoffLocation;
    double distanceInMiles;

public:
    Ride(const std::string& identifier, const std::string& pickup, const std::string& dropoff, double distanceMiles)
        : rideID(identifier), pickupLocation(pickup), dropoffLocation(dropoff), distanceInMiles(distanceMiles)
    {
    }
    virtual ~Ride() = default;

    virtual double fare() const
    {
        return distanceInMiles * baseFareRatePerMile;
    }

    virtual void rideDetails() const
    {
        std::cout << "Ride ID: " << rideID << "\n";
        std::cout << "Pickup: " << pickupLocation << " -> Dropoff: " << dropoffLocation << "\n";
        std::cout << "Distance: " << distanceInMiles << " miles, Fare: $" << fare() << "\n";
    }
};

class StandardRide : public Ride
{
public:
    StandardRide(const std::string& identifier, const std::string& pickup, const std::string& dropoff, double distanceMiles)
        : Ride(identifier, pickup, dropoff, distanceMiles)
    {
    }

    double fare() const override
    {
        return distanceInMiles * standardFareRatePerMile;
    }

    void rideDetails() const override
    {
        std::cout << "[Standard Ride]\n";
        Ride::rideDetails();
    }
};

class PremiumRide : public Ride
{
public:
    PremiumRide(const std::string& identifier, const std::string& pickup, const std::string& dropoff, double distanceMiles)
        : Ride(identifier, pickup, dropoff, distanceMiles)
    {
    }

    double fare() const override
    {
        return distanceInMiles * premiumFareRatePerMile;
    }

    void rideDetails() const override
    {
        std::cout << "[Premium Ride]\n";
        Ride::rideDetails();
    }
};

class Driver
{
private:
    std::string driverID;
    std::string driverName;
    double driverRating;
    std::vector<std::unique_ptr<Ride>> assignedRides;

public:
    Driver(const std::string& identifier, const std::string& name, double rating)
        : driverID(identifier), driverName(name), driverRating(rating)
    {
    }

    void addRide(std::unique_ptr<Ride> rideToAdd)
    {
        if (rideToAdd)
        {
            assignedRides.push_back(std::move(rideToAdd));
        }
    }

    void getDriverInfo() const
    {
        std::cout << "Driver ID: " << driverID << ", Name: " << driverName << ", Rating: " << driverRating << "\n";
        std::cout << "Completed rides: " << assignedRides.size() << "\n";
        for (size_t rideIndex = 0; rideIndex < assignedRides.size(); ++rideIndex)
        {
            std::cout << "--- Ride " << (rideIndex + 1) << " ---\n";
            assignedRides[rideIndex]->rideDetails();
        }
    }
};

class Rider
{
private:
    std::string riderID;
    std::string riderName;
    std::vector<std::unique_ptr<Ride>> requestedRides;

public:
    Rider(const std::string& identifier, const std::string& name)
        : riderID(identifier), riderName(name)
    {
    }

    void requestRide(std::unique_ptr<Ride> rideToAdd)
    {
        if (rideToAdd)
        {
            requestedRides.push_back(std::move(rideToAdd));
        }
    }

    void viewRides() const
    {
        std::cout << "Rider ID: " << riderID << ", Name: " << riderName << "\n";
        std::cout << "Requested rides: " << requestedRides.size() << "\n";
        for (size_t rideIndex = 0; rideIndex < requestedRides.size(); ++rideIndex)
        {
            std::cout << "--- Ride " << (rideIndex + 1) << " ---\n";
            requestedRides[rideIndex]->rideDetails();
        }
    }
};

static void RunPolymorphismDemo()
{
    std::vector<std::unique_ptr<Ride>> rides;
    rides.push_back(std::make_unique<StandardRide>("R001", "Downtown", "Airport", 12.0));
    rides.push_back(std::make_unique<PremiumRide>("R002", "Mall", "Station", 5.0));
    rides.push_back(std::make_unique<StandardRide>("R003", "Hotel", "Convention Center", 3.5));
    rides.push_back(std::make_unique<PremiumRide>("R004", "University", "Downtown", 8.0));

    std::cout << "Fares - Polymorphism will be in effect here deepding on the type of ride:\n";
    for (size_t rideIndex = 0; rideIndex < rides.size(); ++rideIndex)
    {
        std::cout << "  Ride " << (rideIndex + 1) << " fare: $" << rides[rideIndex]->fare() << "\n";
    }

    std::cout << "\nRide details - Polymorphism will be in effect here deepding on the type of ride):\n";
    for (size_t rideIndex = 0; rideIndex < rides.size(); ++rideIndex)
    {
        std::cout << "--- Ride " << (rideIndex + 1) << " ---\n";
        rides[rideIndex]->rideDetails();
    }
}

static void RunDriverAndRiderDemo()
{
    Driver driver("D01", "Arun", 4.8);
    driver.addRide(std::make_unique<StandardRide>("R101", "A St", "B St", 4.0));
    driver.addRide(std::make_unique<PremiumRide>("R102", "C St", "D St", 7.0));
    std::cout << "Driver info:\n";
    driver.getDriverInfo();

    Rider rider("U01", "Kalash");
    rider.requestRide(std::make_unique<StandardRide>("R201", "Home", "Office", 6.0));
    rider.requestRide(std::make_unique<PremiumRide>("R202", "Office", "Airport", 15.0));
    std::cout << "\nRider ride history - Polymorphism will be in effect here deepding on the type of ride):\n";
    rider.viewRides();
}

int main()
{
    std::cout << "Ride Sharing - Demo\n";

    RunPolymorphismDemo();
    RunDriverAndRiderDemo();

    std::cout << "\nDone.\n";
    return 0;
}
