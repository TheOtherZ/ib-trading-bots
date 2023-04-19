#pragma once
#include<iostream>
#include "StdAfx.h"

#include "EWrapper.h"
#include "EReaderOSSignal.h"
#include "EReader.h"

class EClientSocket;

class IbAPI: public EWrapper
{
public:
    IbAPI();
    ~IbAPI();
    void sayHello();

    void setConnectOptions(const std::string&);
    void processMessages();

    bool connect(const char * host, int port, int clientId = 0);
    void disconnect() const;
    bool isConnected() const;

public:
    #define EWRAPPER_VIRTUAL_IMPL {}
    #include "LightningEWrapper_prototypes.h"

private:
    EReaderOSSignal m_osSignal;
    EClientSocket * const m_pClient;

    time_t m_sleepDeadline;

    OrderId m_orderId;
    std::unique_ptr<EReader> m_pReader;
     bool m_extraAuth {false};
};