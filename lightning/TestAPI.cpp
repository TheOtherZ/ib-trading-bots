#include "TestAPI.h"

#include "EClientSocket.h"

TestAPI::TestAPI() :
          m_osSignal(2000)//2-seconds timeout
        , m_pClient(new EClientSocket(this, &m_osSignal))
        , m_sleepDeadline(0)
        // , m_orderId(0)
        {
}

TestAPI::~TestAPI()
{
    // destroy the reader before the client
    // if( m_pReader )
    //     m_pReader.reset();

    delete m_pClient;
}

void TestAPI::sayHello()
{
std::cout << "Hello there" << std::endl;
}