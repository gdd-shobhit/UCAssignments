"""
Syscall-emulation driver for daxpy on X86MinorCPU with configurable FloatSimd
(opLat / issueLat).

Multi-core TLP uses **daxpy_shard** (one independent process per core, same
global problem size n). gem5 SE does not reliably support pthreads; sharding
avoids pthread_create/clone issues.

From the gem5 repo root:
  make -f tests/Makefile.daxpy gem5
  ./build/ALL/gem5.opt -d m5out-daxpy tests/run_daxpy_minor.py \\
      --binary ./tests/daxpy_shard_m5 --num-cpus 4 --op-lat 3 --issue-lat 4

Optional --workload pthread uses daxpy_mt (only reliable with --threads 1 in SE).
"""

import argparse
import os
import sys

import m5
from m5.defines import buildEnv
from m5.objects import (
    AddrRange,
    DDR3_1600_8x8,
    MemCtrl,
    Process,
    Root,
    SEWorkload,
    SrcClockDomain,
    System,
    SystemXBar,
    VoltageDomain,
    X86MinorCPU,
    Cache,
)
from m5.objects.BaseMinorCPU import (
    MinorDefaultFloatSimdFU,
    MinorDefaultIntDivFU,
    MinorDefaultIntFU,
    MinorDefaultIntMulFU,
    MinorDefaultMemFU,
    MinorDefaultMiscFU,
    MinorDefaultPredFU,
    MinorFUPool,
)


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


def make_fu_pool(op_lat: int, issue_lat: int) -> MinorFUPool:
    """One pool per CPU (separate SimObject instances)."""
    return MinorFUPool(
        funcUnits=[
            MinorDefaultIntFU(),
            MinorDefaultIntFU(),
            MinorDefaultIntMulFU(),
            MinorDefaultIntDivFU(),
            MinorDefaultFloatSimdFU(opLat=op_lat, issueLat=issue_lat),
            MinorDefaultPredFU(),
            MinorDefaultMemFU(),
            MinorDefaultMiscFU(),
        ]
    )


def main():
    if not buildEnv.get("USE_X86_ISA", False):
        print("This script requires gem5 built with X86 ISA support.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binary",
        default="./tests/daxpy_shard",
        help="daxpy_shard (default) or daxpy_mt if --workload pthread",
    )
    parser.add_argument(
        "--workload",
        choices=("shard", "pthread"),
        default="shard",
        help="shard: one process per CPU (gem5 SE). pthread: single process "
        "(use --threads 1 in SE)",
    )
    parser.add_argument(
        "--num-cpus",
        type=int,
        default=1,
        help="Number of X86MinorCPU cores",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="pthread count for daxpy_mt only; default = num_cpus",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=262144,
        help="Global vector length (doubles) for all shards / pthread workload",
    )
    parser.add_argument(
        "--op-lat",
        type=int,
        default=6,
        help="FloatSimd MinorFU opLat",
    )
    parser.add_argument(
        "--issue-lat",
        type=int,
        default=1,
        help="FloatSimd MinorFU issueLat",
    )
    parser.add_argument(
        "--mem-size",
        type=str,
        default="512MiB",
        help="Physical memory (increase for very large --n)",
    )
    args = parser.parse_args()

    if args.num_cpus < 1:
        print("--num-cpus must be >= 1", file=sys.stderr)
        sys.exit(1)

    binary = os.path.abspath(args.binary)
    if not os.path.isfile(binary):
        print(f"Binary not found: {binary}", file=sys.stderr)
        sys.exit(1)

    cwd = os.getcwd()

    if args.workload == "pthread" and args.num_cpus != 1:
        print(
            "warning: --workload pthread uses one process on all CPUs; "
            "use --num-cpus 1 or switch to --workload shard for real multi-core TLP",
            file=sys.stderr,
        )

    system = System()
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    system.voltage_domain = VoltageDomain(voltage="1.0V")
    system.cpu_voltage_domain = VoltageDomain(voltage="1.0V")
    system.cpu_clk_domain = SrcClockDomain(
        clock="1GHz", voltage_domain=system.cpu_voltage_domain
    )

    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange(args.mem_size)]

    system.membus = SystemXBar()
    system.system_port = system.membus.cpu_side_ports

    system.cpu = [
        X86MinorCPU(
            cpu_id=i,
            clk_domain=system.cpu_clk_domain,
            executeFuncUnits=make_fu_pool(args.op_lat, args.issue_lat),
        )
        for i in range(args.num_cpus)
    ]

    for cpu in system.cpu:
        cpu.icache = L1ICache()
        cpu.dcache = L1DCache()
        cpu.icache.cpu_side = cpu.icache_port
        cpu.dcache.cpu_side = cpu.dcache_port
        cpu.icache.mem_side = system.membus.cpu_side_ports
        cpu.dcache.mem_side = system.membus.cpu_side_ports
        cpu.createInterruptController()
        cpu.interrupts[0].pio = system.membus.mem_side_ports
        cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
        cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    system.workload = SEWorkload.init_compatible(binary)

    if args.workload == "shard":
        processes = []
        for i in range(args.num_cpus):
            p = Process(pid=100 + i)
            p.executable = binary
            p.cwd = cwd
            p.cmd = [binary, str(i), str(args.num_cpus), str(args.n)]
            p.gid = os.getgid()
            processes.append(p)
        for i, cpu in enumerate(system.cpu):
            cpu.workload = processes[i]
            cpu.createThreads()
        print(
            "daxpy MinorCPU (shard): cpus=%d global_n=%d FloatSimd opLat=%d issueLat=%d"
            % (args.num_cpus, args.n, args.op_lat, args.issue_lat)
        )
    else:
        threads = args.threads if args.threads is not None else args.num_cpus
        if threads < 1:
            print("--threads must be >= 1", file=sys.stderr)
            sys.exit(1)
        process = Process(pid=100)
        process.executable = binary
        process.cwd = cwd
        process.cmd = [binary, str(threads), str(args.n)]
        process.gid = os.getgid()
        for cpu in system.cpu:
            cpu.workload = process
            cpu.createThreads()
        print(
            "daxpy MinorCPU (pthread): cpus=%d threads=%d n=%d "
            "FloatSimd opLat=%d issueLat=%d"
            % (args.num_cpus, threads, args.n, args.op_lat, args.issue_lat)
        )

    root = Root(full_system=False, system=system)
    m5.instantiate()

    exit_event = m5.simulate()
    print(
        "Exiting @ tick %s because %s"
        % (m5.curTick(), exit_event.getCause())
    )


if __name__ == "__m5_main__":
    main()
