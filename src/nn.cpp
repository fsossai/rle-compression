#include <fstream>
#include <iostream>

#include "mhp.h"

using namespace std;

int main(int argc, char *argv[]) {
  if (argc < 3) {
    cout << "Usage: " << argv[0] << " INPUT OUTPUT\n";
    return 1;
  }

  const string input_filename = argv[1];
  const string output_filename = argv[2];

  auto dataframe = DataFrame(input_filename);
  auto path = nearest_neighbor(dataframe);
  auto output_file = ofstream(output_filename);

  output_file << path.to_string("\n") << endl;
  printf("Path exported\n");

  return 0;
}
