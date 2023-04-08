#pragma once
#include<iostream>
#include "StdAfx.h"

#include "EWrapper.h"
#include "EReaderOSSignal.h"
#include "EReader.h"

class EClientSocket;

class TestAPI: public EWrapper
{
public:
    TestAPI();
    ~TestAPI();
    void sayHello();

public:
    #define EWRAPPER_VIRTUAL_IMPL {}
    #include "EWrapper_prototypes.h"

private:
    EReaderOSSignal m_osSignal;
    EClientSocket * const m_pClient;

    time_t m_sleepDeadline;

    // OrderId m_orderId;
    // std::unique_ptr<EReader> m_pReader;
};