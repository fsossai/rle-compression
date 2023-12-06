#include <chrono>

template<class U = std::chrono::milliseconds>
class LTimer {
public:
  LTimer(int64_t interval) {
    restart();
    setInterval(interval);
  }

  void restart() {
    origin_ = std::chrono::high_resolution_clock::now();
    last_ = origin_;
  }

  bool up() {
    using namespace std::chrono;
    auto now = high_resolution_clock::now();
    auto elapsed = duration_cast<U>(
        now - last_).count();
    return elapsed >= interval_;
  }

  bool uplap() {
    if (up()) {
      lap();
      return true;
    }
    return false;
  }

  int64_t lap() {
    using namespace std::chrono;
    auto now = high_resolution_clock::now();
    auto elapsed = duration_cast<U>(
        now - last_).count();
    last_ = now;
    return elapsed;
  }

  int64_t total() {
    using namespace std::chrono;
    auto now = high_resolution_clock::now();
    auto elapsed = duration_cast<U>(
        now - origin_).count();
    return elapsed;
  }

  void setInterval(int64_t interval) {
    if (interval >= 0) {
      interval_ = interval;
    } else {
      interval_ = 0;
    }
  }

  int64_t getInterval() {
    return interval_;
  }

private:
  std::chrono::time_point<std::chrono::high_resolution_clock> origin_;
  std::chrono::time_point<std::chrono::high_resolution_clock> last_;
  int64_t interval_;
};

