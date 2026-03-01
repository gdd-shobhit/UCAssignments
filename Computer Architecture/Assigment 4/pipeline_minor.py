from m5.objects import (
    System,
    SrcClockDomain,
    VoltageDomain,
    AddrRange,
    SystemXBar,
    DDR3_1600_8x8,
    MemCtrl,
    SEWorkload,
    Process,
    X86MinorCPU,
    Cache,
    Root,
)
import m5


class L1ICache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


class L1DCache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


def build_system():
    system = System()

    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange("512MiB")]

    system.cpu = X86MinorCPU()

    system.cpu.icache = L1ICache()
    system.cpu.dcache = L1DCache()

    system.membus = SystemXBar()

    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    system.cpu.icache.mem_side = system.membus.cpu_side_ports
    system.cpu.dcache.mem_side = system.membus.cpu_side_ports

    system.cpu.createInterruptController()
    if hasattr(system.cpu, "interrupts"):
        system.cpu.interrupts[0].pio = system.membus.mem_side_ports
        system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
        system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    system.workload = SEWorkload.init_compatible("./tests/hello")
    process = Process()
    process.cmd = ["./tests/hello"]
    system.cpu.workload = process
    system.cpu.createThreads()

    return system


if __name__ == "__m5_main__":  # gem5 sets this when running the script
    root = Root(full_system=False, system=build_system())
    m5.instantiate()

    print("Beginning MinorCPU pipeline simulation!")
    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

