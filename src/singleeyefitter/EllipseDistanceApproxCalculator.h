#ifndef singleeyefitter_ellipsedistanceapproxcalculator_h__
#define singleeyefitter_ellipsedistanceapproxcalculator_h__

#include "mathHelper.h"

// Calculates:
//     r * (1 - ||A(p - t)||)
//
//          ||A(p - t)||   maps the ellipse to a unit circle
//      1 - ||A(p - t)||   measures signed distance from unit circle edge
// r * (1 - ||A(p - t)||)  scales this to major radius of ellipse, for (roughly) pixel distance
//
// Actually use (r - ||rAp - rAt||) and precalculate r, rA and rAt.

namespace singleeyefitter {

    using math::norm;

    template<typename T>
    class EllipseDistCalculator {
        public:
            EllipseDistCalculator(const Ellipse2D<T>& ellipse) : r(ellipse.major_radius)
            {
                using std::sin;
                using std::cos;
                rA << r* cos(ellipse.angle) / ellipse.major_radius, r* sin(ellipse.angle) / ellipse.major_radius,
                -r* sin(ellipse.angle) / ellipse.minor_radius, r* cos(ellipse.angle) / ellipse.minor_radius;
                rAt = rA * ellipse.center;
            }
            template<typename U>
            T operator()(U&& x, U&& y)
            {
                return calculate(std::forward<U>(x), std::forward<U>(y));
            }

            template<typename U>
            T calculate(U&& x, U&& y)
            {
                T rAxt((rA(0, 0) * x + rA(0, 1) * y) - rAt[0]);
                T rAyt((rA(1, 0) * x + rA(1, 1) * y) - rAt[1]);
                T xy_dist = norm(rAxt, rAyt);
                return (r - xy_dist);
            }
        private:
            Eigen::Matrix<T, 2, 2> rA;
            Eigen::Matrix<T, 2, 1> rAt;
            T r;
    };

} //namespace

#endif //singleeyefitter_ellipsedistanceapproxcalculator_h__
