#include "IbAPI.h"

const unsigned SLEEP_TIME = 10;

int main()
{
    IbAPI IbAPIInstance;

    IbAPIInstance.sayHello();

    bool connection_status = IbAPIInstance.connect("127.0.0.1", 7497, 20);

    printf( "Sleeping %u seconds before disconnecting\n", SLEEP_TIME);
		std::this_thread::sleep_for(std::chrono::seconds(SLEEP_TIME));

    IbAPIInstance.disconnect();
}