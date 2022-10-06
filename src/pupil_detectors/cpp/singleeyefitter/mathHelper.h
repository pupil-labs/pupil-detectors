#ifndef singleeyefitter_math_h__
#define singleeyefitter_math_h__

#include <limits>
#include <list>
#include <Eigen/Core>

namespace singleeyefitter {

    namespace math {

#define MAKE_SQ(TYPE) \
    inline auto sq(TYPE val) -> decltype(val*val) { return val * val; }

        MAKE_SQ(float)
        MAKE_SQ(double)
        MAKE_SQ(long double)
        MAKE_SQ(char)
        MAKE_SQ(short)
        MAKE_SQ(int)
        MAKE_SQ(long)
        MAKE_SQ(long long)
        MAKE_SQ(unsigned char)
        MAKE_SQ(unsigned short)
        MAKE_SQ(unsigned int)
        MAKE_SQ(unsigned long)
        MAKE_SQ(unsigned long long)

#undef MAKE_STD_SQ

        template<typename T>
        inline T round(T value, T precision)  {
            T factor = T(1) / precision;
            return floor( value * factor + 0.5 ) / factor;
        }

        template<typename T, typename TMin, typename TMax>
        inline T clamp(T val, TMin min_val = std::numeric_limits<T>::min(), TMax max_val = std::numeric_limits<T>::max())
        {
            if (min_val > max_val)
                return clamp(val, max_val, min_val);

            if (val <= min_val)
                return min_val;

            if (val >= max_val)
                return max_val;

            return val;
        }

        template<typename T>
        inline T lerp(const T& val1, const T& val2, const T& alpha)
        {
            return val1 * (1.0 - alpha) + val2 * alpha;
        }

        template<typename Scalar, typename T>
        Scalar getAngleABC(const T& a, const T& b, const T& c)
        {
            T ab = { b.x - a.x, b.y - a.y };
            T cb = { b.x - c.x, b.y - c.y };
            Scalar dot = ab.dot(cb); // dot product
            Scalar cross = ab.cross(cb); // cross product
            Scalar alpha = atan2(cross, dot);
            return alpha * Scalar(180.0) / M_PI;
        }

        template<typename T>
        inline T norm(T x, T y)
        {
            using std::sqrt;
            using math::sq;
            return sqrt(sq(x) + sq(y));
        }

        template<typename T>
        Eigen::Matrix<T, 3, 1> sph2cart(T r, T theta, T psi)
        {
            using std::sin;
            using std::cos;
            return r * Eigen::Matrix<T, 3, 1>(sin(theta) * cos(psi), cos(theta), sin(theta) * sin(psi));
        }

        template<typename T>
        Eigen::Matrix<T, 2, 1> cart2sph(T x, T y, T z)
        {
            using std::sin;
            using std::cos;
            using std::sqrt;
            double r =  sqrt( x*x + y*y + z*z);
            double theta = acos( y / r);
            double psi = atan2(z, x );
            return Eigen::Matrix<T, 2, 1>(theta,psi);
        }
         template<typename T>
        Eigen::Matrix<T, 2, 1> cart2sph(const Eigen::Matrix<T, 3, 1>& m )
        {
                return cart2sph<T>( m.x(), m.y(), m.z());
        }

        template <typename T>
        inline int sign(const T& z)
        {
           return (z == 0) ? 0 : (z < 0) ? -1 : 1;
        }

        template<typename T>
        T haversine(T theta1, T psi1, T theta2, T psi2 )
        {
            using std::sin;
            using std::cos;
            using std::acos;
            using std::asin;
            using std::atan2;
            using std::sqrt;
            using singleeyefitter::math::sq;

            if (theta1 == theta2 && psi1 == psi2) {
                return T(0);
            }
            // Haversine distance
            auto dist = T(2) * asin(sqrt( (sin((theta2 - theta1) / T(2))*sin((theta2 - theta1) / T(2))) + cos(theta1) * cos(theta2) * (sin((psi2 - psi1) / T(2))*sin((psi2 - psi1) / T(2))) ));
            return dist;

        }

        template<typename T>
        class SMA{ //simple moving average

            public:

                SMA( int windowSize ) : mWindowSize(windowSize), mAverage(0.0), mAverageDirty(true)
                {};

                void addValue( T value ){
                    mValues.push_back( value );
                    // calculate moving average of value
                    if( mValues.size() <=  mWindowSize || mAverageDirty ){
                        mAverageDirty = false;
                        mAverage = 0.0;
                        for(auto& element : mValues){
                            mAverage += element;
                        }
                        mAverage /= mValues.size();
                    }else{
                        // we can optimize if the wanted window size is reached
                        T first = mValues.front();
                        mValues.pop_front();
                        mAverage += value/mWindowSize - first/mWindowSize;
                    }
                }

                double getAverage() const { return mAverage; };
                int getWindowSize() const { return mWindowSize; };

                void changeWindowSize( int windowSize){

                    if( windowSize < mWindowSize){

                        if( mValues.size() > windowSize )
                            mAverageDirty  = true;
                        while( mValues.size() > windowSize){
                            mValues.pop_front();
                        }

                    }
                    mWindowSize = windowSize;

                }

            private:

            SMA(){};

            std::list<T> mValues;
            int mWindowSize;
            T mAverage;
            bool mAverageDirty; // when we change the window size we need to recalculate from ground up
        };

        template<typename T>
        class WMA{ //weighted moving average

            public:

                WMA( int windowSize ) : mWindowSize(windowSize) , mDenominator(1.0), mNumerator(0.0), mAverage(0.0), mAverageDirty(true)
                {};

                void addValue( T value , T weight ){
                    mValues.emplace_back( value, weight );
                    // calculate weighted moving average of value

                    if( mValues.size() <=  mWindowSize || mAverageDirty){
                        mAverageDirty = false;
                        mDenominator = 0.0;
                        mNumerator = 0.0;
                        for(auto& element : mValues){
                            mNumerator += element.first * element.second;
                            mDenominator += element.second;
                        }
                        mAverage = mNumerator / mDenominator;
                    }else{
                        // we can optimize if the wanted window size is reached
                        auto observation = mValues.front();
                        mValues.pop_front();
                        mDenominator -= observation.second;
                        mDenominator += weight;

                        mNumerator -= observation.first * observation.second;
                        mNumerator += value * weight;
                        mAverage = mNumerator / mDenominator;
                    }

                }

                double getAverage() const { return mAverage; };
                int getWindowSize() const { return mWindowSize; };

                void changeWindowSize( int windowSize){

                    if( windowSize < mWindowSize){

                        if( mValues.size() > windowSize )
                            mAverageDirty  = true;
                        while( mValues.size() > windowSize){
                            mValues.pop_front();
                        }

                    }
                    mWindowSize = windowSize;

                }

            private:

            WMA(){};

            std::list<std::pair<T,T>> mValues;
            int mWindowSize;
            T mDenominator;
            T mNumerator;
            T mAverage;
            bool mAverageDirty;
        };

    } // math namespace

} // singleeyefitter namespace


#endif // singleeyefitter_math_h__
