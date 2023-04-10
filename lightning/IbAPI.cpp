#include "IbAPI.h"

#include "EClientSocket.h"

IbAPI::IbAPI() : m_osSignal(2000)//2-seconds timeout
                   , m_pClient(new EClientSocket(this, &m_osSignal))
                   , m_sleepDeadline(0)
                   , m_orderId(0)
                   , m_extraAuth(false)
{
}

IbAPI::~IbAPI()
{
  // destroy the reader before the client
  if (m_pReader)
    m_pReader.reset();

  delete m_pClient;
}

void IbAPI::setConnectOptions(const std::string& connectOptions)
{
  m_pClient->setConnectOptions(connectOptions);
}

bool IbAPI::connect(const char *host, int port, int clientId)
{
  // trying to connect
  printf("Connecting to %s:%d clientId:%d\n", !(host && *host) ? "127.0.0.1" : host, port, clientId);

  //! [connect]
  bool bRes = m_pClient->eConnect(host, port, clientId, m_extraAuth);
  //! [connect]

  if (bRes)
  {
    printf("Connected to %s:%d clientId:%d\n", m_pClient->host().c_str(), m_pClient->port(), clientId);
    //! [ereader]
    m_pReader = std::unique_ptr<EReader>(new EReader(m_pClient, &m_osSignal));
    m_pReader->start();
    //! [ereader]
  }
  else
    printf("Cannot connect to %s:%d clientId:%d\n", m_pClient->host().c_str(), m_pClient->port(), clientId);

  return bRes;
}

void IbAPI::disconnect() const
{
  m_pClient->eDisconnect();

  printf ( "Disconnected\n");
}

bool IbAPI::isConnected() const
{
  return m_pClient->isConnected();
}

void IbAPI::error(int id, int errorCode, const std::string& errorString, const std::string& advancedOrderRejectJson)
{
    if (!advancedOrderRejectJson.empty()) {
        printf("Error. Id: %d, Code: %d, Msg: %s, AdvancedOrderRejectJson: %s\n", id, errorCode, errorString.c_str(), advancedOrderRejectJson.c_str());
    } else {
        printf("Error. Id: %d, Code: %d, Msg: %s\n", id, errorCode, errorString.c_str());
    }
}

void IbAPI::sayHello()
{
  std::cout << "Hello there" << std::endl;
}