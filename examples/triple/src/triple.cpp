// this program is combined from matmul, raytracer and tsp_ga
#include <algorithm>
#include <assert.h>
#include <iostream>
#include <limits>
#include <math.h>
#include <sstream>
#include <stdio.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <time.h>
#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <fstream>
#include <vector>
#include <iostream>
#include <cassert>

#if defined(__linux__) || defined(__APPLE__)
// "Compiled for Linux
#else
// Windows doesn't define these values by default, Linux does
#define M_PI 3.141592653589793
#define INFINITY 1e8
#endif

#define N 512

template <class T>
T **make_test_matrix()
{
    T **data = new T *[N];
    for (int i = 0; i < N; i++)
    {
        data[i] = new T[N];
    }
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            data[i][j] = (int)i * j;
        }
    }
    return data;
}

template <typename T>
void Transpose(int size, T **__restrict__ m)
{
    for (int i = 0; i < size; i++)
    {
        for (int j = i + 1; j < size; j++)
        {
            std::swap(m[i][j], m[j][i]);
        }
    }
}
template <typename T>
void SeqMatrixMult3(int size, T **__restrict__ m1, T **__restrict__ m2,
                    T **__restrict__ result)
{
    Transpose(size, m2);
    for (int i = 0; i < size; i++)
    {
        for (int j = 0; j < size; j++)
        {
            T c = 0;
            for (int k = 0; k < size; k++)
            {
                c += m1[i][k] * m2[j][k];
            }
            result[i][j] = c;
        }
    }
    Transpose(size, m2);
}

template <typename T>
void test()
{
    T **a = make_test_matrix<T>();
    T **b = make_test_matrix<T>();
    T **c = make_test_matrix<T>();
    SeqMatrixMult3(N, a, b, c);

    T avg = 0;
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            avg += c[i][j] / (T)(N * N);
        }
    }
    // print out average so caller can check answer
    std::cout << avg << std::endl;
}

class TSP
{
public:
    TSP(const double crossoverProbability, const double mutationProbability);

    /* The constants used in this project */
    static const unsigned int chromosones = 30, cities = 20, xMin = 0, xMax = 1000, yMin = 0, yMax = 500;

    /* Generate a random population of chromosones */
    void randomPopulation();

    /* Create a new population using crossover and mutation */
    void nextPopulation();

    /* Returns the fitness of the best chromosone */
    double getBestFitness() const;

    /* Returns a string representation of the best path */
    std::string getBestPathString() const;

    /* Returns the total distance of the best chromosone path */
    double getLowestTotalDistance() const;

    /* Returns the populations average length */
    double getAverageDistance() const;

private:
    const double crossoverProbability, mutationProbability;

    /* Gets the total distance of the supplied path */
    double totalDistance(int const *const chromosone) const;

    /* The coordinates for each city, (x,y) for the first city is found in (citiesX[0], citiesY[0]) */
    double citiesX[cities], citiesY[cities];

    /* The chromosone containing the shortest path */
    int *bestChromosone;

    /* Contains the current population of chromosones */
    int (*solutions)[cities],
        /* The two chromosones with the best fitness functions */
        // bestChromosone1[cities], bestChromosone2[cities],
        /* Used to store the new chromosones when creating a new population */
        (*newPopulation)[cities];

    /* Returns a random double r, 0 <= r <= max */
    static double randomInclusive(const double max);

    /* Returns a random double r, 0 <= r < max */
    static double randomExclusive(const double max);

    /* True if the two chromosones represent the same path */
    static bool areChromosonesEqual(int const *const chromosoneA, int const *const chromosoneB);

    /* Evaluate the fitness the supplied chromosone */
    double evaluateFitness(const int *const chromosone) const;

    /* Selects a chromosone from the current population using Roulette Wheel Selection.
     * Using the algorithm described in http://www.obitko.com/tutorials/genetic-algorithms/selection.php.
     */
    int *rouletteSelection(double const *const fitness) const;

    /* Replace the element at offspringIndex with the first element found in other that does not exist in offspringToRepair */
    void repairOffspring(int *const offspringToRepair, int missingIndex, const int *const other);

    /* Might swap one gene with another, depending on the mutation probability */
    void mutate(int *const chromosone);

    /* Cross over the parents to form new offspring using Multi-Point Crossover, collisions are handled as shown in lecture 5.
     * The chromosones might be a copy of their parents, depending on the crossover probability.
     */
    void crossover(const int *const parentA, const int *const parentB, int *const offspringA, int *const offspringB);

    /* Checks if the supplied chromosone is in newPopulation */
    bool hasDuplicate(const int *const chromosone, size_t populationCount);

    /* Copies the supplied chromosone to the new population */
    void copyToNewPopulation(const int *const chromosone, size_t index);

    /* Make the chromosone represent a path, which is chosen by random */
    static void setRandomPath(int *const chromosone);
};

using namespace std;

TSP::TSP(double crossoverProbability, double mutationProbability) : crossoverProbability(crossoverProbability),
                                                                    mutationProbability(mutationProbability), solutions(new int[chromosones][cities]), newPopulation(new int[chromosones][cities])
{
    /* Seed the random number generator */
    // srand((unsigned int)time(NULL));
    srand(17);
    /* Use the same number to generate a specific sequence */
    // srand(0);
    /* Set random coordinates */
    for (size_t coordinateIndex = 0; coordinateIndex < cities; ++coordinateIndex)
    {
        /* 0 <= x <= xMax */
        citiesX[coordinateIndex] = randomInclusive(xMax);
        /* 0 <= y <= yMax */
        citiesY[coordinateIndex] = randomInclusive(yMax);
    }

    /* Generate random population */
    randomPopulation();
}

void TSP::randomPopulation()
{
    /* Iterate throught each chromosone... */
    for (size_t chromosoneIndex = 0; chromosoneIndex < chromosones; ++chromosoneIndex)
    {
        /* ... and give it a random path */
        setRandomPath(solutions[chromosoneIndex]);
    }
}

double TSP::getBestFitness() const
{
    return evaluateFitness(bestChromosone);
}

double TSP::getAverageDistance() const
{
    double distance = 0;
    for (size_t chromosoneIndex = 0; chromosoneIndex < chromosones; ++chromosoneIndex)
    {
        distance += totalDistance(solutions[chromosoneIndex]);
    }
    return distance / chromosones;
}

string TSP::getBestPathString() const
{
    stringstream path;
    for (size_t gene = 0; gene < cities; ++gene)
    {
        if (gene != 0)
        {
            path << ",";
        }
        path << bestChromosone[gene];
    }
    return path.str();
}

double TSP::getLowestTotalDistance() const
{
    return totalDistance(bestChromosone);
}

void TSP::nextPopulation()
{
    double fitness[chromosones];
    /* Fill an array with a fitness score for each chromosone,
     * the index of a score corresponds with the chromosone's index in solutions[index]
     */
    for (size_t chromosoneIndex = 0; chromosoneIndex < chromosones; ++chromosoneIndex)
    {
        fitness[chromosoneIndex] = evaluateFitness(solutions[chromosoneIndex]);
    }

    /* Use elitism, find and copy over the two best chromosones to the new population */
    int eliteIndex1 = 0, eliteIndex2 = 0;
    /* find the best solution */
    eliteIndex1 = max_element(fitness, fitness + chromosones) - fitness;
    this->bestChromosone = solutions[eliteIndex1];

    double highestFitness = 0;
    /* Find the second best solution */
    for (size_t chromosoneIndex = 0; chromosoneIndex < chromosones; ++chromosoneIndex)
    {
        if (chromosoneIndex != eliteIndex1 && fitness[chromosoneIndex] > highestFitness)
        {
            highestFitness = fitness[chromosoneIndex];
            eliteIndex2 = chromosoneIndex;
        }
    }

    /* Keep track of how many chromosones exists in the new population */
    size_t offspringCount = 0;
    /* Copy over the two best solutions to the new population */
    copyToNewPopulation(solutions[eliteIndex1], offspringCount);
    ++offspringCount;
    copyToNewPopulation(solutions[eliteIndex2], offspringCount);
    ++offspringCount;

    /* Create the rest of the new population, break this loop when the new population is complete */
    while (true)
    {
        int *parentA;
        int *parentB;
        parentA = rouletteSelection(fitness);
        parentB = rouletteSelection(fitness);
        while (parentB == parentA)
        {
            parentB = rouletteSelection(fitness);
        }
        int offspringA[cities];
        int offspringB[cities];
        crossover(parentA, parentB, offspringA, offspringB);
        mutate(offspringA);
        mutate(offspringB);

        /* Add to new population if an equal chromosone doesn't exist already */
        if (!hasDuplicate(offspringA, offspringCount))
        {
            copyToNewPopulation(offspringA, offspringCount);
            ++offspringCount;
        }
        /* We need to check if the new population is filled */
        if (offspringCount == chromosones)
        {
            break;
        }
        if (!hasDuplicate(offspringB, offspringCount))
        {
            copyToNewPopulation(offspringB, offspringCount);
            ++offspringCount;
        }
        /* Check again so that we don't accidentaly write all over the heap and have to spend an evening wondering why the heap is corrupt... :) */
        if (offspringCount == chromosones)
        {
            break;
        }
    }

    /*
     * We now have a new population,
     * now it needs to replace the current population
     * so that we don't go through the same population every time we run this function
     */
    for (size_t chromosoneIndex = 0; chromosoneIndex < chromosones; ++chromosoneIndex)
    {
        memcpy(solutions[chromosoneIndex], newPopulation[chromosoneIndex], sizeof(int) * cities);
    }
}

bool TSP::hasDuplicate(const int *const chromosone, size_t populationCount)
{
    /* Iterate throught each chromosone in newPopulation and compare them gene by gene */
    for (size_t chromosoneIndex = 0; chromosoneIndex < populationCount; ++chromosoneIndex)
    {
        int genesCompared = 0;
        for (size_t gene = 0; gene < cities; ++gene)
        {
            if (chromosone[gene] != newPopulation[chromosoneIndex][gene])
            {
                /* These chromosones are not equal! */
                break;
            }
            ++genesCompared;
        }

        if (genesCompared == cities)
        {
            return true;
        }
    }

    return false;
}

void TSP::mutate(int *const chromosone)
{
    /* 0.0 <= random <= 1 */
    {
        double random = randomInclusive(1);
        /* Nope, didn't happen */
        if (random > mutationProbability)
        {
            return;
        }
    }

    int tmp;
    int random1 = (int)randomExclusive(cities);
    int random2 = (int)randomExclusive(cities);
    while (random1 == random2)
    {
        random2 = (int)randomExclusive(cities);
    }

    tmp = chromosone[random1];
    chromosone[random1] = chromosone[random2];
    chromosone[random2] = tmp;
}

void TSP::crossover(int const *const parentA, const int *const parentB, int *offspringA, int *offspringB)
{
    {
        /* There is a chance we don't perform a crossover,
         * in that case the offspring is a copy of the parents
         */
        /* 0.0 <= random <= 1 */
        double random = randomInclusive(1);
        /* The offspring is a copy of their parents */
        if (random > crossoverProbability)
        {
            memcpy(offspringA, parentA, sizeof(int) * cities);
            memcpy(offspringB, parentB, sizeof(int) * cities);
            return;
        }
    }
    /* Perform multi-point crossover to generate offspring */

    /* 0 <= cuttOffIndex <= cities */
    int cuttOffIndex1 = (int)randomInclusive(cities);
    int cuttOffIndex2 = (int)randomInclusive(cities);
    while (cuttOffIndex2 == cuttOffIndex1)
    {
        cuttOffIndex2 = (int)randomExclusive(cities);
    }

    unsigned int start;
    unsigned int end;
    if (cuttOffIndex1 < cuttOffIndex2)
    {
        start = cuttOffIndex1;
        end = cuttOffIndex2;
    }
    else
    {
        start = cuttOffIndex2;
        end = cuttOffIndex1;
    }
    /* Offspring A is initially copy of parent A */
    memcpy(offspringA, parentA, sizeof(int) * cities);
    /* Offspring B is initially copy of parent B */
    memcpy(offspringB, parentB, sizeof(int) * cities);

    /* Put a sequence of parent B in offspring A */
    memcpy(offspringA + start, parentB + start, sizeof(int) * (end - start));
    /* Put a sequence of parent A in offspring B */
    memcpy(offspringB + start, parentA + start, sizeof(int) * (end - start));

    /* Mark collisions in offspring with -1*/
    for (size_t cityIndex = 0; cityIndex < cities; ++cityIndex)
    {
        /* Index is part of the parent sequence */
        if ((cityIndex >= start && cityIndex < end))
        {
            /* Do nothing, we want to keep this sequence intact */
        }
        else
        {
            /* Check if the item at cityIndex also occurs somewhere in the copied substring */
            for (size_t substringIndex = start; substringIndex < end; ++substringIndex)
            {
                /* A duplicate, mark it */
                if (offspringA[cityIndex] == offspringA[substringIndex])
                {
                    offspringA[cityIndex] = -1;
                }
                if (offspringB[cityIndex] == offspringB[substringIndex])
                {
                    offspringB[cityIndex] = -1;
                }
            }
        }
    }

    /*
     * Go through the offspring,
     * if an element is marked we fill the hole with an element from the other offspring
     */
    for (size_t offspringIndex = 0; offspringIndex < cities; ++offspringIndex)
    {
        /* There is a hole here */
        if (offspringA[offspringIndex] == -1)
        {
            repairOffspring(offspringA, offspringIndex, offspringB);
        }
        if (offspringB[offspringIndex] == -1)
        {
            repairOffspring(offspringB, offspringIndex, offspringA);
        }
    }
}

void TSP::repairOffspring(int *const offspringToRepair, int missingIndex, const int *const other)
{
    /* Iterate through the other offspring until we find an element which doesn't exist in the offspring we are repairing */
    for (size_t patchIndex = 0; patchIndex < cities; ++patchIndex)
    {
        /* Look for other[patchIndex] in offspringToRepair */
        int *missing = find(offspringToRepair, offspringToRepair + cities, other[patchIndex]);

        /* The element at other[patchIndex] is missing from offspringToRepair */
        if (missing == (offspringToRepair + cities))
        {
            // cout << "1:" << offspringToRepair[missingIndex] << endl;
            offspringToRepair[missingIndex] = other[patchIndex];
            // cout << "2:" << offspringToRepair[missingIndex] << endl;
            break;
        }
    }
}

void TSP::copyToNewPopulation(int const *const chromosone, size_t index)
{
    assert(index < chromosones && "Index out of bounds");
    for (size_t i = 0; i < cities; ++i)
    {
        newPopulation[index][i] = chromosone[i];
    }
}

int *TSP::rouletteSelection(double const *const fitness) const
{
    double sum = 0;
    /* Calculate sum of all chromosome fitnesses in population */
    for (size_t i = 0; i < chromosones; ++i)
    {
        sum += fitness[i];
    }

    /* 0.0 <= random <= sum */
    double random = randomInclusive(sum);

    sum = 0;
    /* Go through the population and sum fitnesses from 0 to sum s. When the sum s is greater or equal to r; stop and return the chromosome where you are */
    for (size_t i = 0; i < chromosones; ++i)
    {
        sum += fitness[i];
        if (sum >= random)
        {
            return solutions[i];
        }
    }
    assert(false && "A chromosone should have been picked by now");
    return (NULL);
}

void TSP::setRandomPath(int *chromosone)
{
    for (size_t i = 0; i < cities; ++i)
    {
        chromosone[i] = i;
    }

    /*
     * Shuffle the chromosone using the Fisher�Yates shuffle.
     */
    for (size_t i = cities - 1; i > 0; --i)
    {
        /* 0 <= random <= i */
        int random = (int)randomInclusive(i);
        int temp = chromosone[i];
        chromosone[i] = chromosone[random];
        chromosone[random] = temp;
    }
}

double TSP::evaluateFitness(int const *const chromosone) const
{
    return 1 / totalDistance(chromosone);
}

double TSP::totalDistance(int const *const chromosone) const
{
    double distance = 0;
    /* Calculate the total distance between all cities */
    for (size_t i = 0; i < cities - 1; ++i)
    {
        double dx = citiesX[chromosone[i]] - citiesX[chromosone[i + 1]];
        double dy = citiesY[chromosone[i]] - citiesY[chromosone[i + 1]];

        /* The distance between two points is the square root of (dx^2+dy^2) */
        distance += sqrt((pow(dx, 2.0) + pow(dy, 2.0)));
    }
    /* We complete the tour by adding the distance between the last and the first city */
    double dx = citiesX[chromosone[cities - 1]] - citiesX[chromosone[0]];
    double dy = citiesY[chromosone[cities - 1]] - citiesY[chromosone[0]];
    distance += sqrt((pow(dx, 2.0) + pow(dy, 2.0)));

    return distance;
}

double TSP::randomInclusive(double max)
{
    /* Generate random number r, 0.0 <= r <= max */
    // return ((double)rand() / (double)RAND_MAX * max);
    return ((double)rand() * max) / (double)RAND_MAX;
}

double TSP::randomExclusive(double max)
{
    /* Generate random number r, 0.0 <= r < max */
    // return ((double)rand() / ((double)RAND_MAX + 1) * max);
    return ((double)rand() * max) / ((double)RAND_MAX + 1);
}

template <typename T>
class Vec3
{
public:
    T x, y, z;
    Vec3() : x(T(0)), y(T(0)), z(T(0)) {}
    Vec3(T xx) : x(xx), y(xx), z(xx) {}
    Vec3(T xx, T yy, T zz) : x(xx), y(yy), z(zz) {}
    Vec3 &normalize()
    {
        T nor2 = length2();
        if (nor2 > 0)
        {
            T invNor = 1 / sqrt(nor2);
            x *= invNor, y *= invNor, z *= invNor;
        }
        return *this;
    }
    Vec3<T> operator*(const T &f) const { return Vec3<T>(x * f, y * f, z * f); }
    Vec3<T> operator*(const Vec3<T> &v) const { return Vec3<T>(x * v.x, y * v.y, z * v.z); }
    T dot(const Vec3<T> &v) const { return x * v.x + y * v.y + z * v.z; }
    Vec3<T> operator-(const Vec3<T> &v) const { return Vec3<T>(x - v.x, y - v.y, z - v.z); }
    Vec3<T> operator+(const Vec3<T> &v) const { return Vec3<T>(x + v.x, y + v.y, z + v.z); }
    Vec3<T> &operator+=(const Vec3<T> &v)
    {
        x += v.x, y += v.y, z += v.z;
        return *this;
    }
    Vec3<T> &operator*=(const Vec3<T> &v)
    {
        x *= v.x, y *= v.y, z *= v.z;
        return *this;
    }
    Vec3<T> operator-() const { return Vec3<T>(-x, -y, -z); }
    T length2() const { return x * x + y * y + z * z; }
    T length() const { return sqrt(length2()); }
    friend std::ostream &operator<<(std::ostream &os, const Vec3<T> &v)
    {
        os << "[" << v.x << " " << v.y << " " << v.z << "]";
        return os;
    }
};

template <typename T>
class Sphere
{
public:
    Vec3<T> center;                      /// position of the sphere
    T radius, radius2;                   /// sphere radius and radius^2
    Vec3<T> surfaceColor, emissionColor; /// surface color and emission (light)
    T transparency, reflection;          /// surface transparency and reflectivity
    Sphere(const Vec3<T> &c, const T &r, const Vec3<T> &sc,
           const T &refl = 0, const T &transp = 0, const Vec3<T> &ec = 0) : center(c), radius(r), radius2(r * r), surfaceColor(sc), emissionColor(ec),
                                                                            transparency(transp), reflection(refl)
    {
    }
    // compute a ray-sphere intersection using the geometric solution
    bool intersect(const Vec3<T> &rayorig, const Vec3<T> &raydir, T *t0 = NULL, T *t1 = NULL) const
    {
        Vec3<T> l = center - rayorig;
        T tca = l.dot(raydir);
        if (tca < 0)
            return false;
        T d2 = l.dot(l) - tca * tca;
        if (d2 > radius2)
            return false;
        T thc = sqrt(radius2 - d2);
        if (t0 != NULL && t1 != NULL)
        {
            *t0 = tca - thc;
            *t1 = tca + thc;
        }

        return true;
    }
};

#define MAX_RAY_DEPTH 5

template <typename T>
T mix(const T &a, const T &b, const T &mix)
{
    return b * mix + a * (T(1) - mix);
}

// This is the main trace function. It takes a ray as argument (defined by its origin
// and direction). We test if this ray intersects any of the geometry in the scene.
// If the ray intersects an object, we compute the intersection point, the normal
// at the intersection point, and shade this point using this information.
// Shading depends on the surface property (is it transparent, reflective, diffuse).
// The function returns a color for the ray. If the ray intersects an object that
// is the color of the object at the intersection point, otherwise it returns
// the background color.
template <typename T>
Vec3<T> trace(const Vec3<T> &rayorig, const Vec3<T> &raydir,
              const std::vector<Sphere<T> *> &spheres, const int &depth)
{
    // if (raydir.length() != 1) std::cerr << "Error " << raydir << std::endl;
    T tnear = INFINITY;
    const Sphere<T> *sphere = NULL;
    // find intersection of this ray with the sphere in the scene
    for (unsigned i = 0; i < spheres.size(); ++i)
    {
        T t0 = INFINITY, t1 = INFINITY;
        if (spheres[i]->intersect(rayorig, raydir, &t0, &t1))
        {
            if (t0 < 0)
                t0 = t1;
            if (t0 < tnear)
            {
                tnear = t0;
                sphere = spheres[i];
            }
        }
    }
    // if there's no intersection return black or background color
    if (!sphere)
        return Vec3<T>(2);
    Vec3<T> surfaceColor = 0;                // color of the ray/surfaceof the object intersected by the ray
    Vec3<T> phit = rayorig + raydir * tnear; // point of intersection
    Vec3<T> nhit = phit - sphere->center;    // normal at the intersection point
    nhit.normalize();                        // normalize normal direction
    // If the normal and the view direction are not opposite to each other
    // reverse the normal direction. That also means we are inside the sphere so set
    // the inside bool to true. Finally reverse the sign of IdotN which we want
    // positive.
    T bias = 1e-4; // add some bias to the point from which we will be tracing
    bool inside = false;
    if (raydir.dot(nhit) > 0)
        nhit = -nhit, inside = true;
    if ((sphere->transparency > 0 || sphere->reflection > 0) && depth < MAX_RAY_DEPTH)
    {
        T facingratio = -raydir.dot(nhit);
        // change the mix value to tweak the effect
        T fresneleffect = mix<T>(pow(1 - facingratio, 3), 1, 0.1);
        // compute reflection direction (not need to normalize because all vectors
        // are already normalized)
        Vec3<T> refldir = raydir - nhit * 2 * raydir.dot(nhit);
        refldir.normalize();
        Vec3<T> reflection = trace(phit + nhit * bias, refldir, spheres, depth + 1);
        Vec3<T> refraction = 0;
        // if the sphere is also transparent compute refraction ray (transmission)
        if (sphere->transparency)
        {
            T ior = 1.1, eta = (inside) ? ior : 1 / ior; // are we inside or outside the surface?
            T cosi = -nhit.dot(raydir);
            T k = 1 - eta * eta * (1 - cosi * cosi);
            Vec3<T> refrdir = raydir * eta + nhit * (eta * cosi - sqrt(k));
            refrdir.normalize();
            refraction = trace(phit - nhit * bias, refrdir, spheres, depth + 1);
        }
        // the result is a mix of reflection and refraction (if the sphere is transparent)
        surfaceColor = (reflection * fresneleffect +
                        refraction * (1 - fresneleffect) * sphere->transparency) *
                       sphere->surfaceColor;
    }
    else
    {
        // it's a diffuse object, no need to raytrace any further
        for (unsigned i = 0; i < spheres.size(); ++i)
        {
            if (spheres[i]->emissionColor.x > 0)
            {
                // this is a light
                Vec3<T> transmission = 1;
                Vec3<T> lightDirection = spheres[i]->center - phit;
                lightDirection.normalize();
                for (unsigned j = 0; j < spheres.size(); ++j)
                {
                    if (i != j)
                    {
                        T t0, t1;
                        if (spheres[j]->intersect(phit + nhit * bias, lightDirection, &t0, &t1))
                        {
                            transmission = 0;
                            break;
                        }
                    }
                }
                surfaceColor += sphere->surfaceColor * transmission *
                                std::max(T(0), nhit.dot(lightDirection)) * spheres[i]->emissionColor;
            }
        }
    }

    return surfaceColor + sphere->emissionColor;
}

// Main rendering function. We compute a camera ray for each pixel of the image
// trace it and return a color. If the ray hits a sphere, we return the color of the
// sphere at the intersection point, else we return the background color.
template <typename T>
unsigned int render(const std::vector<Sphere<T> *> &spheres)
{
    unsigned width = 640, height = 480;
    Vec3<T> *image = new Vec3<T>[width * height], *pixel = image;
    T invWidth = 1 / T(width), invHeight = 1 / T(height);
    T fov = 30, aspectratio = width / T(height);
    T angle = tan(M_PI * 0.5 * fov / T(180));
    // Trace rays
    for (unsigned y = 0; y < height; ++y)
    {
        for (unsigned x = 0; x < width; ++x, ++pixel)
        {
            T xx = (2 * ((x + 0.5) * invWidth) - 1) * angle * aspectratio;
            T yy = (1 - 2 * ((y + 0.5) * invHeight)) * angle;
            Vec3<T> raydir(xx, yy, -1);
            raydir.normalize();
            *pixel = trace(Vec3<T>(0), raydir, spheres, 0);
        }
    }
#if 0
	// Save result to a PPM image (keep these flags if you compile under Windows)
	std::ofstream ofs("./untitled.ppm", std::ios::out | std::ios::binary);
	ofs << "P6\n" << width << " " << height << "\n255\n";
	for (unsigned i = 0; i < width * height; ++i) {
		ofs << (unsigned char)(std::min(T(1), image[i].x) * 255) << 
		(unsigned char)(std::min(T(1), image[i].y) * 255) <<
		(unsigned char)(std::min(T(1), image[i].z) * 255); 
	}
	ofs.close();
#endif

    unsigned int bad_hash = 0;
    for (unsigned i = 0; i < width * height; ++i)
    {
        bad_hash = bad_hash * 31 + (unsigned int)(std::min(T(1), image[i].x) * 255);
        bad_hash = bad_hash * 31 + (unsigned int)(std::min(T(1), image[i].y) * 255);
        bad_hash = bad_hash * 31 + (unsigned int)(std::min(T(1), image[i].z) * 255);
    }
    delete[] image;

    return bad_hash;
}

volatile unsigned int dont_optimize_me;

int main(int argc, const char *argv[])
{
    /* 90% mutation probability, 2% mutation probability */
    TSP *tsp = new TSP(0.9, 0.02);
    size_t generations = 0, generationsWithoutImprovement = 0;
    double bestFitness = -1;
    double initialAverage = tsp->getAverageDistance();
    /* We'll stop when we've gone 10k generations without improvement */
    while (generations < 10000)
    {
        tsp->nextPopulation();
        ++generations;
        double newFitness = tsp->getBestFitness();
        /* The new fitness is higher, the chromosone is better */
        if (newFitness > bestFitness)
        {
            bestFitness = newFitness;
            generationsWithoutImprovement = 0;
            // cout << "Best goal function: " << tsp->getBestFitness() << endl;
        }
        else
        {
            ++generationsWithoutImprovement;
        }
    }
    // cout << "DONE!" << endl;
    cout << "Number of generations: " << generations << endl;
    cout << "Best chromosone info: " << endl;
    cout << "\t-Path: " << tsp->getBestPathString() << endl;
    cout << "\t-Goal function: " << tsp->getBestFitness() << endl;
    cout << "\t-Distance: " << tsp->getLowestTotalDistance() << endl;
    cout << "Average distance: " << tsp->getAverageDistance() << endl;
    cout << "Initial average: " << initialAverage << endl;
    delete tsp;
    srand48(13);
    std::vector<Sphere<float> *> spheres;
    // position, radius, surface color, reflectivity, transparency, emission color
    spheres.push_back(new Sphere<float>(Vec3<float>(0, -10004, -20), 10000, Vec3<float>(0.2), 0, 0.0));
    spheres.push_back(new Sphere<float>(Vec3<float>(0, 0, -20), 4, Vec3<float>(1.00, 0.32, 0.36), 1, 0.5));
    spheres.push_back(new Sphere<float>(Vec3<float>(5, -1, -15), 2, Vec3<float>(0.90, 0.76, 0.46), 1, 0.0));
    spheres.push_back(new Sphere<float>(Vec3<float>(5, 0, -25), 3, Vec3<float>(0.65, 0.77, 0.97), 1, 0.0));
    spheres.push_back(new Sphere<float>(Vec3<float>(-5.5, 0, -15), 3, Vec3<float>(0.90, 0.90, 0.90), 1, 0.0));
    // light
    spheres.push_back(new Sphere<float>(Vec3<float>(0, 20, -30), 3, Vec3<float>(0), 0, 0, Vec3<float>(3)));

    dont_optimize_me = render<float>(spheres);
    __asm__ __volatile__("" ::
                             : "memory"); // memory barrier
    if (dont_optimize_me == 0x4bd7c0e0)
    {
        // printf("CORRECT\n");
    }
    else
    {
        printf("ERROR: WRONG ANSWER\n");
    }

    while (!spheres.empty())
    {
        Sphere<float> *sph = spheres.back();
        spheres.pop_back();
        delete sph;
    }
    test<float>();
    return 0;
}
