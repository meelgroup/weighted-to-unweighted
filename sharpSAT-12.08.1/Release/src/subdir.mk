################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/basic_types.cpp \
../src/component_management.cpp \
../src/component_types.cpp \
../src/instance.cpp \
../src/main.cpp \
../src/solver.cpp 

OBJS += \
./src/basic_types.o \
./src/component_management.o \
./src/component_types.o \
./src/instance.o \
./src/main.o \
./src/solver.o 

CPP_DEPS += \
./src/basic_types.d \
./src/component_management.d \
./src/component_types.d \
./src/instance.d \
./src/main.d \
./src/solver.d 

#g++ -L/opt/apps/gmp/5.0.4/lib/ -I/opt/apps/gmp/5.0.4/include/ -O3 -g -pg -Wall -std=c++0x -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++  -L/home/kgm2/Experimentation/Scripts/INSTALL/gmp/lib/ -I/home/kgm2/Experimentation/Scripts/INSTALL/gmp/include/ -O3 -g -pg -Wall -std=c++0x -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


