#include <fstream>
#include <iostream>

#include "mhp.h"

using namespace std;

int main(int argc, char *argv[]) {
  if (argc < 4) {
    cout << "Usage: " << argv[0] << " INPUT OUTPUT TIME_LIMIT\n";
    return 1;
  }

  const string input_filename = argv[1];
  const string output_filename = argv[2];
  const int time_limit = atoi(argv[3]) * 1'000; // [ms]

  auto dataframe = DataFrame(input_filename);
  auto path = Path(dataframe);
  path.initialize();
  vns(path, time_limit);
  auto output_file = ofstream(output_filename);

  output_file << path.to_string("\n") << endl;
  printf("Path exported\n");

  return 0;
}
