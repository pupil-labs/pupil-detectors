#ifndef __UTILS_H__
#define __UTILS_H__

#include "geometry/Ellipse.h"
#include "geometry/Circle.h"
#include "geometry/Sphere.h"
#include "common/constants.h"
#include "mathHelper.h"

#include <string>
#include <vector>
#include <set>
#include <sstream>
#include <stdexcept>

#include <iostream>

#include <Eigen/Core>
#include <opencv2/core.hpp>

namespace singleeyefitter {

    int random(int min, int max);
    int random(int min, int max, unsigned int seed);
    double random(double min, double max);
    double random(double min, double max, unsigned int seed);

    template<typename Scalar>
    inline Eigen::Matrix<Scalar, 2, 1> toEigen(const cv::Point2f& point)
    {
        return Eigen::Matrix<Scalar, 2, 1>(static_cast<Scalar>(point.x),
                                           static_cast<Scalar>(point.y));
    }
    template<typename Scalar>
    inline cv::Point2f toPoint2f(const Eigen::Matrix<Scalar, 2, 1>& point)
    {
        return cv::Point2f(static_cast<float>(point[0]),
                           static_cast<float>(point[1]));
    }
    template<typename Scalar>
    inline cv::Point toPoint(const Eigen::Matrix<Scalar, 2, 1>& point)
    {
        return cv::Point(static_cast<int>(point[0]),
                         static_cast<int>(point[1]));
    }
    template<typename Scalar>
    inline cv::Mat toMat(const Eigen::Matrix<Scalar, 3, 1>& point)
    {
        return (cv::Mat_<Scalar>(3,1) << point[0],
                                         point[1],
                                         point[2]);
    }
    template<typename Scalar>
    inline cv::Mat toMat(const Eigen::Matrix<Scalar, 2, 1>& point)
    {
        return (cv::Mat_<Scalar>(2,1) << point[0],
                                         point[1]);
    }
    template<typename Scalar>
    inline cv::RotatedRect toRotatedRect(const Ellipse2D<Scalar>& ellipse)
    {
        return cv::RotatedRect(toPoint2f(ellipse.center),
                               cv::Size2f(static_cast<float>(2.0 * ellipse.major_radius),
                                          static_cast<float>(2.0 * ellipse.minor_radius)),
                               static_cast<float>(ellipse.angle * 180.0 / constants::PI));
    }
    template<typename Scalar>
    inline Ellipse2D<Scalar> toEllipse(const cv::RotatedRect& rect)
    {
        // Scalar major = rect.size.height;
        // Scalar minor = rect.size.width;
        // if(major < minor ){
        //     std::cout << "Flip major minor !!" << std::endl;
        //     std::swap(major,minor);
        // }
        return Ellipse2D<Scalar>(toEigen<Scalar>(rect.center),
                                 static_cast<Scalar>(rect.size.height / 2.0),
                                 static_cast<Scalar>(rect.size.width / 2.0),
                                 static_cast<Scalar>((rect.angle + 90.0) * constants::PI / 180.0));
    }

        template<typename Scalar>
    cv::Rect bounding_box(const Ellipse2D<Scalar>& ellipse)
    {
        using std::sin;
        using std::cos;
        using std::sqrt;
        using std::floor;
        using std::ceil;
        Scalar ux = ellipse.major_radius * cos(ellipse.angle);
        Scalar uy = ellipse.major_radius * sin(ellipse.angle);
        Scalar vx = ellipse.minor_radius * cos(ellipse.angle + constants::PI / 2);
        Scalar vy = ellipse.minor_radius * sin(ellipse.angle + constants::PI / 2);
        Scalar bbox_halfwidth = sqrt(ux * ux + vx * vx);
        Scalar bbox_halfheight = sqrt(uy * uy + vy * vy);
        return cv::Rect(floor(ellipse.center[0] - bbox_halfwidth), floor(ellipse.center[1] - bbox_halfheight),
                        2 * ceil(bbox_halfwidth) + 1, 2 * ceil(bbox_halfheight) + 1);
    }

} //namespace singleeyefitter

#endif // __UTILS_H__
