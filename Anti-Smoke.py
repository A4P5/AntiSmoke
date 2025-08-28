import pymem


"""Disables the ability for smoke grenades to deploy - by writing into cs2 memory"""

pm = pymem.Pymem("cs2.exe")
client_process = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll


# offsets last updated - 14:54-28.08.2025
m_pEntity = 16               #  ("CEntityInstance", "m_pEntity")
m_designerName = 32          #  m.client("CEntityIdentity", "m_designerName")
m_bDidSmokeEffect = 5244     #  ("C_SmokeGrenadeProjectile", "m_bDidSmokeEffect")
dwEntityList = 30473736      #  m.offset("dwEntityList")


def read_string(address, max_size=260):
    if not address:
        return ""
    result = bytearray()

    for i in range(max_size):
        try:
            ch = pm.read_bytes(address + i, 1)
        except:
            break  # stop if memory is not accessible

        if ch == b"\x00":
            break
        result.extend(ch)

    return result.decode(errors="ignore")


while True:
    entityList = pm.read_longlong(client_process + dwEntityList)

    for i in range(64, 1024):
        try:
            uListEntry = pm.read_ulonglong(
                entityList + (0x8 * ((i & 0x7FFF) >> 0x9)) + 0x10
            )
        except:
            continue

        if not uListEntry:
            continue
        try:
            Entity = pm.read_ulonglong(uListEntry + 0x78 * (i & 0x1FF))
            if not Entity:
                continue
        except:
            continue
        entityIdentityAddress = pm.read_ulonglong(Entity + m_pEntity)
        if not entityIdentityAddress:
            continue
        designerNameAddress = pm.read_ulonglong(
            entityIdentityAddress + m_designerName)
        if not designerNameAddress:
            continue
        if not read_string(designerNameAddress, 260) == 'smokegrenade_projectile':
            continue

        if pm.read_longlong(Entity + m_bDidSmokeEffect) == 0:

            pm.write_longlong(Entity + m_bDidSmokeEffect, 1)

    time.sleep(0.01)
