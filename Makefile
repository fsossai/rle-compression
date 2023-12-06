CC=clang++
OPT=-O3
FLAGS=-Wall
EL= # -ferror-limit=1
STD=-std=c++2a # minimum: c++17

MHP_SOURCES=mhp.cpp path.cpp dataframe.cpp matrix.cpp

all: nn.out vns.out ml.out

%.out: nn.cpp $(MHP_SOURCES)
	$(CC) $(STD) $(OPT) $(FLAGS) $(EL) $^ -o $@

#vns: vns.cpp $(MHP_SOURCES)
#	$(CC) $(STD) $(OPT) $(FLAGS) $(EL) $^ -o $@
#
#ml: ml.cpp $(MHP_SOURCES)
#	$(CC) $(STD) $(OPT) $(FLAGS) $(EL) $^ -o $@
